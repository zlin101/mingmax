import httpx

from app.llm.base import LLMClient


class LLMClientError(RuntimeError):
    pass


class LLMClientConfigError(LLMClientError):
    pass


class OpenAICompatibleLLMClient(LLMClient):
    SUPPORTED_WIRE_APIS = {"chat_completions", "responses"}

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        wire_api: str = "chat_completions",
        timeout_seconds: int = 30,
    ) -> None:
        missing = [
            name
            for name, value in {
                "llm_api_key": api_key,
                "llm_base_url": base_url,
                "llm_model": model,
            }.items()
            if not value.strip()
        ]
        if missing:
            raise LLMClientConfigError(f"Missing LLM config: {', '.join(missing)}")

        if wire_api not in self.SUPPORTED_WIRE_APIS:
            supported = ", ".join(sorted(self.SUPPORTED_WIRE_APIS))
            raise LLMClientConfigError(f"Unsupported LLM wire API: {wire_api}. Supported values: {supported}")

        if timeout_seconds <= 0:
            raise LLMClientConfigError("LLM timeout must be greater than 0")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._wire_api = wire_api
        self._timeout = timeout_seconds

    async def generate(self, prompt: str, context: str = "") -> str:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self._url(), headers=self._headers(), json=self._payload(prompt, context))
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
        except ValueError as e:
            raise LLMClientError("LLM response invalid JSON") from e

        try:
            content = self._extract_content(body)
        except (KeyError, IndexError, TypeError) as e:
            raise LLMClientError(f"LLM response missing text: {e}") from e

        if not content or not content.strip():
            raise LLMClientError("LLM returned empty content")

        return content.strip()

    def _url(self) -> str:
        if self._wire_api == "responses":
            return f"{self._base_url}/responses"
        return f"{self._base_url}/chat/completions"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _payload(self, prompt: str, context: str) -> dict[str, object]:
        if self._wire_api == "responses":
            input_text = f"{context}\n\n{prompt}" if context else prompt
            return {"model": self._model, "input": input_text}

        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        return {"model": self._model, "messages": messages}

    def _extract_content(self, body: object) -> str:
        if self._wire_api == "responses":
            return self._extract_responses_content(body)
        return self._extract_chat_completions_content(body)

    def _extract_chat_completions_content(self, body: object) -> str:
        if not isinstance(body, dict):
            raise TypeError("response body is not an object")
        content = body["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("message content is not a string")
        return content

    def _extract_responses_content(self, body: object) -> str:
        if not isinstance(body, dict):
            raise TypeError("response body is not an object")

        output_text = body.get("output_text")
        if isinstance(output_text, str):
            return output_text

        for item in body["output"]:
            if not isinstance(item, dict):
                raise TypeError("response output item is not an object")
            for content_item in item["content"]:
                if not isinstance(content_item, dict):
                    raise TypeError("response content item is not an object")
                text = content_item.get("text")
                if isinstance(text, str):
                    return text

        raise KeyError("output_text")
