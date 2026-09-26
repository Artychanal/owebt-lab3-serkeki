import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.ai_client import AIServiceError, GeminiClient
from app.keyboards import main_menu
from app.texts import (
    AI_BUTTON,
    AI_PROMPT_TEXT,
    CONTACTS_BUTTON,
    CONTACTS_TEXT,
    STUDENT_BUTTON,
    STUDENT_TEXT,
    TECHNOLOGIES_BUTTON,
    TECHNOLOGIES_TEXT,
    WELCOME_TEXT,
)

logger = logging.getLogger(__name__)
router = Router()

MAX_PROMPT_LENGTH = 4000
TELEGRAM_MESSAGE_LIMIT = 4000


class AIRequest(StatesGroup):
    waiting_for_prompt = State()


def split_message(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    """Split a long answer into Telegram-safe chunks, preferring newlines."""
    chunks: list[str] = []
    remaining = text.strip()

    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = remaining.rfind(" ", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    if remaining:
        chunks.append(remaining)
    return chunks


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    await state.clear()
    text = "Запит скасовано." if current_state else "Немає активного запиту."
    await message.answer(text, reply_markup=main_menu())


@router.message(F.text == STUDENT_BUTTON)
async def student_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(STUDENT_TEXT, reply_markup=main_menu())


@router.message(F.text == TECHNOLOGIES_BUTTON)
async def technologies_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(TECHNOLOGIES_TEXT, reply_markup=main_menu())


@router.message(F.text == CONTACTS_BUTTON)
async def contacts_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(CONTACTS_TEXT, reply_markup=main_menu())


@router.message(F.text == AI_BUTTON)
async def ai_prompt_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(AIRequest.waiting_for_prompt)
    await message.answer(AI_PROMPT_TEXT)


@router.message(AIRequest.waiting_for_prompt, F.text)
async def ai_answer_handler(
    message: Message, state: FSMContext, ai_client: GeminiClient
) -> None:
    prompt = message.text.strip()
    if not prompt:
        await message.answer("Запит не може бути порожнім.")
        return
    if len(prompt) > MAX_PROMPT_LENGTH:
        await message.answer(
            f"Запит надто довгий. Максимум — {MAX_PROMPT_LENGTH} символів."
        )
        return

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    try:
        answer = await ai_client.ask(prompt)
    except AIServiceError as error:
        logger.exception("Gemini request failed")
        await message.answer(str(error), reply_markup=main_menu())
        await state.clear()
        return

    await state.clear()
    for chunk in split_message(answer):
        await message.answer(chunk, parse_mode=None, reply_markup=main_menu())


@router.message(AIRequest.waiting_for_prompt)
async def non_text_prompt_handler(message: Message) -> None:
    await message.answer("Будь ласка, надішліть текстовий запит.")


@router.message()
async def unknown_handler(message: Message) -> None:
    await message.answer(
        "Я не розпізнав повідомлення. Скористайтеся меню або командою /start.",
        reply_markup=main_menu(),
    )

