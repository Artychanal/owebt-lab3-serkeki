import pytest

from app.config import ConfigError, load_settings


def test_load_settings_for_polling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("RUN_MODE", "polling")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    settings = load_settings()

    assert settings.run_mode == "polling"
    assert settings.gemini_model == "gemini-3.5-flash-lite"


def test_webhook_requires_https(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:test-token")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("RUN_MODE", "webhook")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "http://example.com")
    monkeypatch.setenv("WEBHOOK_SECRET", "valid-secret")

    with pytest.raises(ConfigError, match="HTTPS"):
        load_settings()
