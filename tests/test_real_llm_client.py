import json

import httpx
import pytest

from app.llm.openai_compatible import LLMClientConfigError, LLMClientError, OpenAICompatibleLLMClient


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


async def test_generate_sends_chat_completion_payload(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "分析结果"}}]},
    )

    await client.generate(prompt="分析命盘", context="命盘数据")

    request = httpx_mock.get_request()
    payload = json.loads(request.read())

    assert request.headers["authorization"] == "Bearer test-key"
    assert payload == {
        "model": "test-model",
        "messages": [{"role": "system", "content": "命盘数据"}, {"role": "user", "content": "分析命盘"}],
    }


async def test_generate_success_without_context(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "结果"}}]},
    )

    result = await client.generate(prompt="测试")
    assert "结果" in result


async def test_generate_responses_success(httpx_mock) -> None:
    responses_client = OpenAICompatibleLLMClient(
        api_key="test-key",
        base_url="https://api.example.com/v1",
        model="test-model",
        wire_api="responses",
        timeout_seconds=5,
    )
    httpx_mock.add_response(
        url="https://api.example.com/v1/responses",
        json={"output_text": "响应结果"},
    )

    result = await responses_client.generate(prompt="分析命盘", context="命盘数据")
    request = httpx_mock.get_request()
    payload = json.loads(request.read())

    assert result == "响应结果"
    assert payload == {"model": "test-model", "input": "命盘数据\n\n分析命盘"}


async def test_generate_responses_nested_output_success(httpx_mock) -> None:
    responses_client = OpenAICompatibleLLMClient(
        api_key="test-key",
        base_url="https://api.example.com/v1",
        model="test-model",
        wire_api="responses",
    )
    httpx_mock.add_response(
        url="https://api.example.com/v1/responses",
        json={"output": [{"content": [{"type": "output_text", "text": "嵌套结果"}]}]},
    )

    result = await responses_client.generate(prompt="分析命盘")
    assert result == "嵌套结果"


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


async def test_generate_invalid_json(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        content=b"not-json",
    )

    with pytest.raises(LLMClientError, match="invalid JSON"):
        await client.generate(prompt="test")


async def test_generate_empty_content(client: OpenAICompatibleLLMClient, httpx_mock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "   "}}]},
    )

    with pytest.raises(LLMClientError, match="empty content"):
        await client.generate(prompt="test")


def test_missing_required_config_raises_config_error() -> None:
    with pytest.raises(LLMClientConfigError, match="llm_api_key"):
        OpenAICompatibleLLMClient(api_key="", base_url="https://api.example.com/v1", model="test-model")


def test_unsupported_wire_api_raises_config_error() -> None:
    with pytest.raises(LLMClientConfigError, match="Unsupported LLM wire API"):
        OpenAICompatibleLLMClient(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="test-model",
            wire_api="unknown",
        )


def test_invalid_timeout_raises_config_error() -> None:
    with pytest.raises(LLMClientConfigError, match="timeout"):
        OpenAICompatibleLLMClient(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="test-model",
            timeout_seconds=0,
        )
