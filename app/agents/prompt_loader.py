from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptLoadError(RuntimeError):
    pass


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise PromptLoadError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")
