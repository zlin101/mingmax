import json

import pytest

from app.agents.ziwei_analysis_agent import (
    LLMOutputParseError,
    ZiweiAnalysisAgent,
    _parse_json_array,
    _parse_json_object,
)
from app.llm.base import LLMClient
from app.schemas.chart import NormalizedChart


class _StubLLMClient(LLMClient):
    def __init__(self, response: str) -> None:
        self._response = response

    async def generate(self, prompt: str, context: str = "") -> str:
        return self._response


def _normalized_chart() -> NormalizedChart:
    return NormalizedChart(chart_id="test-chart", source="test", summary="test chart")


# --- _parse_json_object ---


def test_parse_json_object_valid() -> None:
    result = _parse_json_object('{"key": "value"}')
    assert result == {"key": "value"}


def test_parse_json_object_with_code_block() -> None:
    result = _parse_json_object('```json\n{"key": "value"}\n```')
    assert result == {"key": "value"}


def test_parse_json_object_invalid_json() -> None:
    with pytest.raises(LLMOutputParseError, match="not valid JSON"):
        _parse_json_object("not json at all")


def test_parse_json_object_returns_array() -> None:
    with pytest.raises(LLMOutputParseError, match="not a JSON object"):
        _parse_json_object("[1, 2, 3]")


def test_parse_json_object_empty_string() -> None:
    with pytest.raises(LLMOutputParseError, match="not valid JSON"):
        _parse_json_object("")


# --- _parse_json_array ---


def test_parse_json_array_valid() -> None:
    result = _parse_json_array('[{"q": "a"}]')
    assert result == [{"q": "a"}]


def test_parse_json_array_with_code_block() -> None:
    result = _parse_json_array('```json\n[{"q": "a"}]\n```')
    assert result == [{"q": "a"}]


def test_parse_json_array_invalid_json() -> None:
    with pytest.raises(LLMOutputParseError, match="not valid JSON"):
        _parse_json_array("not json")


def test_parse_json_array_returns_object() -> None:
    with pytest.raises(LLMOutputParseError, match="not a JSON array"):
        _parse_json_array('{"key": "value"}')


# --- Agent.analyze ---


async def test_agent_analyze_valid_json() -> None:
    llm = _StubLLMClient(
        json.dumps(
            {
                "summary": "test summary",
                "strong_signals": ["s1"],
                "weak_hypotheses": ["h1"],
                "cross_checks": ["c1"],
                "safety_note": "safe",
            }
        )
    )
    agent = ZiweiAnalysisAgent(llm)
    result = await agent.analyze(_normalized_chart())

    assert result.summary == "test summary"
    assert result.strong_signals == ["s1"]
    assert result.weak_hypotheses == ["h1"]
    assert result.cross_checks == ["c1"]
    assert result.safety_note == "safe"


async def test_agent_analyze_non_json() -> None:
    llm = _StubLLMClient("This is plain text, not JSON")
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="not valid JSON"):
        await agent.analyze(_normalized_chart())


async def test_agent_analyze_missing_required_fields() -> None:
    llm = _StubLLMClient(json.dumps({"summary": "ok"}))
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="missing required fields"):
        await agent.analyze(_normalized_chart())


async def test_agent_analyze_json_array_instead_of_object() -> None:
    llm = _StubLLMClient('[{"summary": "wrong"}]')
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="not a JSON object"):
        await agent.analyze(_normalized_chart())


# --- Agent.analyze_themes ---


async def test_agent_analyze_themes_valid_json() -> None:
    llm = _StubLLMClient(
        json.dumps(
            {
                "theme": "career",
                "observations": ["obs1"],
                "supporting_evidence": ["ev1"],
                "uncertainty": "some uncertainty",
                "followup_questions": ["fq1"],
            }
        )
    )
    agent = ZiweiAnalysisAgent(llm)
    results = await agent.analyze_themes(_normalized_chart(), ["career"])

    assert len(results) == 1
    assert results[0].theme == "career"
    assert results[0].observations == ["obs1"]


async def test_agent_analyze_themes_non_json() -> None:
    llm = _StubLLMClient("plain text")
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="not valid JSON"):
        await agent.analyze_themes(_normalized_chart(), ["career"])


async def test_agent_analyze_themes_missing_fields() -> None:
    llm = _StubLLMClient(json.dumps({"theme": "relationship"}))
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="missing required fields"):
        await agent.analyze_themes(_normalized_chart(), ["relationship"])


# --- Agent.generate_followup_questions ---


async def test_agent_followup_questions_valid_json() -> None:
    llm = _StubLLMClient(
        json.dumps(
            [
                {
                    "question": "q1",
                    "reason": "r1",
                    "related_chart_factors": ["f1"],
                },
                {
                    "question": "q2",
                    "reason": "r2",
                    "related_chart_factors": [],
                },
            ]
        )
    )
    agent = ZiweiAnalysisAgent(llm)
    results = await agent.generate_followup_questions(_normalized_chart(), "test analysis")

    assert len(results) == 2
    assert results[0].question == "q1"
    assert results[1].reason == "r2"


async def test_agent_followup_questions_non_json() -> None:
    llm = _StubLLMClient("plain text")
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="not valid JSON"):
        await agent.generate_followup_questions(_normalized_chart(), "analysis")


async def test_agent_followup_questions_json_object_instead_of_array() -> None:
    llm = _StubLLMClient(json.dumps({"question": "wrong"}))
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="not a JSON array"):
        await agent.generate_followup_questions(_normalized_chart(), "analysis")


async def test_agent_followup_questions_array_item_not_object() -> None:
    llm = _StubLLMClient(json.dumps(["string_item"]))
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="not a JSON object"):
        await agent.generate_followup_questions(_normalized_chart(), "analysis")


async def test_agent_followup_questions_missing_fields() -> None:
    llm = _StubLLMClient(json.dumps([{}]))
    agent = ZiweiAnalysisAgent(llm)

    with pytest.raises(LLMOutputParseError, match="missing required fields"):
        await agent.generate_followup_questions(_normalized_chart(), "analysis")
