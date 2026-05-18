from app.api.dependencies import _get_llm_client
from app.llm.mock import MockLLMClient
from app.llm.openai_compatible import OpenAICompatibleLLMClient


def test_provider_mock_returns_mock_client(monkeypatch) -> None:
    monkeypatch.delenv("MINGMAX_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MINGMAX_LLM_API_KEY", raising=False)
    monkeypatch.delenv("MINGMAX_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("MINGMAX_LLM_MODEL", raising=False)
    monkeypatch.delenv("MINGMAX_LLM_TIMEOUT_SECONDS", raising=False)

    client = _get_llm_client()
    assert isinstance(client, MockLLMClient)


def test_provider_openai_compatible_returns_real_client(monkeypatch) -> None:
    monkeypatch.setenv("MINGMAX_LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("MINGMAX_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("MINGMAX_LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("MINGMAX_LLM_MODEL", "gpt-4")
    monkeypatch.setenv("MINGMAX_LLM_TIMEOUT_SECONDS", "15")

    client = _get_llm_client()
    assert isinstance(client, OpenAICompatibleLLMClient)
    assert client._model == "gpt-4"
    assert client._timeout == 15
