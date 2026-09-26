import pytest

from app.config import ConfigError, load_settings


def test_load_settings_for_polling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("RUN_MODE", "polling")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)

    settings = load_settings()

    assert settings.run_mode == "polling"
    assert settings.gemini_model == "gemini-3.5-flash-lite"


def test_allowed_user_ids_are_parsed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("RUN_MODE", "polling")
    monkeypatch.setenv("ALLOWED_USER_IDS", "686381696, 123456789")

    settings = load_settings()

    assert settings.allowed_user_ids == frozenset({686381696, 123456789})


def test_webhook_requires_https(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("RUN_MODE", "webhook")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "http://example.com")
    monkeypatch.setenv("WEBHOOK_SECRET", "valid-secret")
    monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)

    with pytest.raises(ConfigError, match="HTTPS"):
        load_settings()


def test_render_url_overrides_stale_manual_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("RUN_MODE", "webhook")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "https://old-service.onrender.com")
    monkeypatch.setenv(
        "RENDER_EXTERNAL_URL", "https://lab3-telegram-ai-bot.onrender.com"
    )
    monkeypatch.setenv("WEBHOOK_SECRET", "valid-secret")

    settings = load_settings()

    assert settings.webhook_url == (
        "https://lab3-telegram-ai-bot.onrender.com/telegram/webhook"
    )
