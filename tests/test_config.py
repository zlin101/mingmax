from app.core.config import Settings, get_settings


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("MINGMAX_APP_NAME", raising=False)
    monkeypatch.delenv("MINGMAX_APP_VERSION", raising=False)
    monkeypatch.delenv("MINGMAX_DEBUG", raising=False)
    monkeypatch.delenv("MINGMAX_HOST", raising=False)
    monkeypatch.delenv("MINGMAX_PORT", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_name == "mingmax"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_get_settings_returns_settings(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("MINGMAX_APP_NAME", raising=False)
    monkeypatch.delenv("MINGMAX_APP_VERSION", raising=False)
    monkeypatch.delenv("MINGMAX_DEBUG", raising=False)
    monkeypatch.delenv("MINGMAX_HOST", raising=False)
    monkeypatch.delenv("MINGMAX_PORT", raising=False)
    monkeypatch.chdir(tmp_path)

    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.app_name == "mingmax"
