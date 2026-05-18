import httpx

from app.llm.base import LLMClient


class LLMClientError(RuntimeError):
    pass


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(self, api_key: str, base_url: str, model: str, timeout_seconds: int = 30) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout_seconds

    async def generate(self, prompt: str, context: str = "") -> str:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": self._model, "messages": messages},
                )
        except httpx.TimeoutException as e:
            raise LLMClientError(f"LLM request timed out: {e}") from e
        except httpx.RequestError as e:
            raise LLMClientError(f"LLM request failed: {e}") from e

        if response.status_code == 401 or response.status_code == 403:
            raise LLMClientError(f"LLM auth failed (HTTP {response.status_code})")

        if response.status_code >= 500:
            raise LLMClientError(f"LLM server error (HTTP {response.status_code})")

        if response.status_code != 200:
            raise LLMClientError(f"LLM unexpected status (HTTP {response.status_code})")

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMClientError(f"LLM response missing text: {e}") from e

        if not content or not content.strip():
            raise LLMClientError("LLM returned empty content")

        return content.strip()
