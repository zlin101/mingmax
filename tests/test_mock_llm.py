from app.llm.base import LLMClient
from app.llm.mock import DISCLAIMER, MockLLMClient


async def test_mock_llm_returns_fixed_content() -> None:
    client = MockLLMClient()
    result = await client.generate(prompt="test", context="ctx")
    assert isinstance(result, str)
    assert len(result) > 0


async def test_mock_llm_is_llm_client() -> None:
    client = MockLLMClient()
    assert isinstance(client, LLMClient)


def test_disclaimer_constant_exists() -> None:
    assert "文化研究" in DISCLAIMER
    assert "不构成" in DISCLAIMER
