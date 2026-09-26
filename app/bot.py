import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from app.ai_client import GeminiClient
from app.config import ConfigError, Settings, load_settings
from app.handlers import router
from app.middlewares import AccessMiddleware


def create_components(settings: Settings) -> tuple[Bot, Dispatcher]:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    dispatcher.message.outer_middleware(
        AccessMiddleware(settings.allowed_user_ids)
    )
    dispatcher.include_router(router)
    dispatcher["ai_client"] = GeminiClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )
    return bot, dispatcher


async def run_polling(settings: Settings) -> None:
    bot, dispatcher = create_components(settings)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


def create_webhook_app(settings: Settings) -> web.Application:
    bot, dispatcher = create_components(settings)
    app = web.Application()

    async def health_handler(_: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def on_startup(_: web.Application) -> None:
        await bot.set_webhook(
            url=settings.webhook_url,
            secret_token=settings.webhook_secret,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )

    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.on_startup.append(on_startup)

    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        handle_in_background=True,
        secret_token=settings.webhook_secret,
    ).register(app, path=settings.webhook_path)
    setup_application(app, dispatcher, bot=bot)
    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    try:
        settings = load_settings()
    except ConfigError as error:
        raise SystemExit(f"Configuration error: {error}") from error

    if settings.run_mode == "webhook":
        web.run_app(create_webhook_app(settings), port=settings.port)
    else:
        asyncio.run(run_polling(settings))


if __name__ == "__main__":
    main()
