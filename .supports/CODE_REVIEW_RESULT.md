# Code Review And Acceptance Result

> 本文件用于保存最近一次 Codex code review 与任务验收结果。每次复审后应完全覆盖本文件，保持内容只代表最新结论。

## Code Review Summary

- Branch: `feature/v0.1-rich-chart-facts-and-decadal-analysis`
- Overall assessment: `APPROVE`
- Files reviewed: 17 tracked files plus this review result file
- Diff size: 870 insertions / 157 deletions
- Review date: 2026-05-24

## Verification

- `git status -sb`: branch has expected Branch 16/17 working-tree changes; `.supports/CODE_REVIEW_RESULT.md` is untracked because Codex created it for latest review handoff.
- `uv run black --check .`: passed
- `uv run isort --check-only .`: passed
- `uv run flake8 .`: passed
- `uv run pytest -q`: passed, `292 passed`

Additional real-runtime inspection:

```text
raw_current_decadal: start_age=26 end_age=35 heavenly_stem='jiHeavenly' earthly_branch='maoEarthly' palace_index=1 palace_name='福德宫'
palace_name_at_idx: 福德宫
facts_current_decadal: {'start_age': 26, 'end_age': 35, 'heavenly_stem': 'jiHeavenly', 'earthly_branch': 'maoEarthly', 'palace_name': '福德宫'}
evidence_match: [{'id': 'decadal:1:26-35', 'type': 'decadal', 'label': '福德宫26-35岁大限'}]
```

## Findings

### P0 - Critical

None.

### P1 - High

None.

### P2 - Medium

1. `app/engines/providers/iztro_provider.py:92` - current-context calculation still depends directly on `datetime.now()`.

   This is acceptable for this branch because Branch 16/17 is adding current大限 context, but it means `current_age/current_decadal` are date-dependent while `chart_id` remains based on birth input only.

   Recommended follow-up:

   - introduce an explicit `analysis_date` contract if the product needs reproducible historical analyses;
   - or extract current-context calculation into a helper that accepts `today` for deterministic tests.

2. `app/engines/providers/iztro_provider.py:141` - current decadal extraction silently falls back to `None` for provider shape errors.

   The code now catches narrower exceptions than before, which is an improvement. Still, since current大限 is part of this branch's stated capability, future work should avoid silent loss of this field.

   Recommended follow-up:

   - extract provider current-context parsing into a small helper;
   - add structured logging if enrichment fails;
   - keep hard assertions in tests so regression is caught.

### P3 - Low

1. Some newly added provider code contains explanatory comments that are a bit more verbose than the project default. This is not blocking, but future cleanup can reduce comments after the logic is stabilized.

## Fixed Since Previous Review

- `five_elements_class` is read from `chart.five_elements_class` and verified at runtime.
- `current_decadal` is populated through the real `chart.horoscope(solar_date)` API.
- `current_decadal.palace_name` now uses the translated Chinese palace name.
- Tests now assert `current_decadal` is present and semantically consistent with the palace-level decadal facts.
- Prompt constraints now allow metadata facts as background while prohibiting BaZi/four-pillars analysis.
- `.supports/API_SPEC.md` and `.supports/ARCHITECTURE.md` document the new metadata, decadal, scope, and evidence contracts.

## Removal/Iteration Plan

No removal required in this branch.

Recommended follow-up after merge:

- make current-context calculation explicitly date-aware;
- isolate provider enrichment helpers to keep `build_chart_from_iztro()` smaller;
- add logging for optional provider enrichment failures.

## Acceptance Result

Accepted.

Branch 16/17 now satisfies the intended scope: `iztro-py` provider facts are absorbed more richly, star scope and metadata are exposed, palace-level decadal facts are included, current decadal context is populated and consistent with evidence IDs, prompts allow 大限区间级 analysis while still blocking 流年/流月/流日/流时 and BaZi expansion, and validator evidence handling supports decadal/metadata IDs.

## Next Action

Recommended action: Claude can commit and push this branch. Merge should still be done only by the project owner.
