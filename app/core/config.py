from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "mingmax"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    llm_provider: str = "mock"
    llm_model: str = "mock"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_wire_api: str = "chat_completions"
    llm_timeout_seconds: int = 30

    model_config = {"env_prefix": "MINGMAX_", "env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    return Settings()
