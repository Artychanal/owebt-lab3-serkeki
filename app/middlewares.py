from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class AccessMiddleware(BaseMiddleware):
    """Allow messages only from explicitly configured Telegram users."""

    def __init__(self, allowed_user_ids: frozenset[int]) -> None:
        self._allowed_user_ids = allowed_user_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # An empty list keeps local development backwards-compatible. The
        # Render Blueprint always supplies the owner's ID.
        if not self._allowed_user_ids:
            return await handler(event, data)

        if isinstance(event, Message):
            user = event.from_user
            if user is None or user.id not in self._allowed_user_ids:
                await event.answer("⛔ У вас немає доступу до цього бота.")
                return None

        return await handler(event, data)

