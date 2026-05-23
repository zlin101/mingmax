import asyncio

from app.engines.chart_diff import ChartDiffResult, PalaceDiff
from scripts.verify_e2e_real_sample import _run_pipeline
from scripts.verify_private_chart_sample import _count_mismatched_palaces, _parse_reference


def test_parse_reference_extracts_multibracket_four_hua_markers() -> None:
    text = """
├基本信息
│ ├性别 : 女
│ ├地理经度 : 121.500
│ ├钟表时间 : 2001-02-03 04:05
│ └身宫:午
├命盘十二宫
│ ├命  宫[甲子]
│ │ ├主星 : 紫微[庙][生年禄],天机[旺][生年忌]
│ │
│ ├兄弟宫[乙丑]
│ │ ├主星 : 太阴[旺][生年权]
│ │
│ └夫妻宫[丙寅][身宫]
│   ├主星 : 文昌[庙][生年科]
"""

    parsed = _parse_reference(text)

    assert parsed["gender"] == "female"
    assert parsed["clock_time"] == "2001-02-03T04:05"
    assert parsed["longitude"] == 121.5
    assert parsed["hua_lu"] == "紫微"
    assert parsed["hua_quan"] == "太阴"
    assert parsed["hua_ke"] == "文昌"
    assert parsed["hua_ji"] == "天机"


def test_count_mismatched_palaces_counts_unique_palace_indexes() -> None:
    result = ChartDiffResult(
        diffs=[
            PalaceDiff(
                palace_index=0,
                palace_name="命宫",
                field="major_stars",
                expected="A",
                actual="B",
                severity="error",
            ),
            PalaceDiff(
                palace_index=0,
                palace_name="命宫",
                field="is_body_palace",
                expected="True",
                actual="False",
                severity="warning",
            ),
            PalaceDiff(
                palace_index=-1,
                palace_name="",
                field="hua_lu",
                expected="A",
                actual="B",
                severity="error",
            ),
        ]
    )

    assert _count_mismatched_palaces(result) == 1


def test_e2e_script_output_contains_no_private_data() -> None:
    from datetime import datetime, timedelta, timezone

    from app.schemas.birth import BirthInfo

    birth_info = BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(2001, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Redacted",
        timezone="Asia/Shanghai",
        longitude=121.5,
    )
    result = asyncio.run(_run_pipeline(birth_info, use_mock=True))
    import json

    output = json.dumps(result, ensure_ascii=False)
    for sensitive in ["2001-02-03", "04:05", "121.5", "Redacted", "female"]:
        assert sensitive not in output, f"Sensitive data '{sensitive}' found in e2e output"


def test_e2e_script_returns_structured_result() -> None:
    from datetime import datetime, timedelta, timezone

    from app.schemas.birth import BirthInfo

    birth_info = BirthInfo(
        calendar_type="solar",
        birth_datetime=datetime(2004, 3, 6, 16, 20, tzinfo=timezone(timedelta(hours=8))),
        gender="female",
        birth_place="Redacted",
        timezone="Asia/Shanghai",
        longitude=113.264,
    )
    result = asyncio.run(_run_pipeline(birth_info, use_mock=True))
    assert "chart_source" in result
    assert "validation_issues" in result
    assert "issue_count" in result
    assert result["llm_mode"] == "mock"


def test_e2e_script_reports_clear_error_for_missing_file() -> None:
    import subprocess

    result = subprocess.run(
        ["uv", "run", "python", "scripts/verify_e2e_real_sample.py", "/nonexistent/file.md", "--mock-llm"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "File not found" in result.stderr or "not found" in result.stderr.lower()


def test_e2e_real_client_imports_correctly() -> None:
    from unittest.mock import MagicMock, patch

    with patch("app.core.config.Settings") as mock_settings_cls:
        mock_settings = MagicMock()
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_base_url = "http://localhost:1234"
        mock_settings.llm_model = "test-model"
        mock_settings.llm_wire_api = "chat_completions"
        mock_settings.llm_timeout_seconds = 10
        mock_settings_cls.return_value = mock_settings

        from app.llm.openai_compatible import OpenAICompatibleLLMClient

        client = OpenAICompatibleLLMClient(
            api_key=mock_settings.llm_api_key,
            base_url=mock_settings.llm_base_url,
            model=mock_settings.llm_model,
            wire_api=mock_settings.llm_wire_api,
            timeout_seconds=mock_settings.llm_timeout_seconds,
        )
        assert client is not None
