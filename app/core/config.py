from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "mingmax"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_prefix": "MINGMAX_", "env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()
