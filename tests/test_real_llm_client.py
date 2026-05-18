import httpx
import pytest

from app.llm.openai_compatible import LLMClientError, OpenAICompatibleLLMClient


def _success_response(content: str) -> httpx.Response:
    body = {"choices": [{"message": {"content": content}}]}
    return httpx.Response(200, json=body)


@pytest.fixture
def client() -> OpenAICompatibleLLMClient:
    return OpenAICompatibleLLMClient(
        api_key="test-key",
        base_url="https://api.example.com/v1",
        model="test-model",
        timeout_seconds=5,
    )


async def test_generate_success(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "分析结果"}}]},
    )

    result = await client.generate(prompt="分析命盘", context="命盘数据")
    assert result == "分析结果"


async def test_generate_success_without_context(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "结果"}}]},
    )

    result = await client.generate(prompt="测试")
    assert "结果" in result


async def test_generate_401(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(url="https://api.example.com/v1/chat/completions", status_code=401)

    with pytest.raises(LLMClientError, match="auth failed"):
        await client.generate(prompt="test")


async def test_generate_403(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(url="https://api.example.com/v1/chat/completions", status_code=403)

    with pytest.raises(LLMClientError, match="auth failed"):
        await client.generate(prompt="test")


async def test_generate_500(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(url="https://api.example.com/v1/chat/completions", status_code=500)

    with pytest.raises(LLMClientError, match="server error"):
        await client.generate(prompt="test")


async def test_generate_timeout(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_exception(httpx.TimeoutException("timed out"))

    with pytest.raises(LLMClientError, match="timed out"):
        await client.generate(prompt="test")


async def test_generate_network_error(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_exception(httpx.ConnectError("connection refused"))

    with pytest.raises(LLMClientError, match="request failed"):
        await client.generate(prompt="test")


async def test_generate_missing_content(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{}]},
    )

    with pytest.raises(LLMClientError, match="missing text"):
        await client.generate(prompt="test")


async def test_generate_empty_content(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "   "}}]},
    )

    with pytest.raises(LLMClientError, match="empty content"):
        await client.generate(prompt="test")
