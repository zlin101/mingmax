from app.core.config import Settings, get_settings


def test_settings_defaults() -> None:
    settings = Settings()

    assert settings.app_name == "mingmax"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_get_settings_returns_settings() -> None:
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.app_name == "mingmax"
