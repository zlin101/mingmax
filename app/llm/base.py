from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: str = "") -> str:
        pass
