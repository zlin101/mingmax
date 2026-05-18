import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(autouse=True)
def force_mock_llm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MINGMAX_LLM_PROVIDER", "mock")


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
