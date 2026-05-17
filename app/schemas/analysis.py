from pydantic import BaseModel


class ThemeAnalysis(BaseModel):
    theme: str
    observations: list[str] = []
    supporting_evidence: list[str] = []
    uncertainty: str | None = None
    followup_questions: list[str] = []


class FollowupQuestion(BaseModel):
    question: str
    reason: str
    related_chart_factors: list[str] = []


class AnalysisResult(BaseModel):
    summary: str
    strong_signals: list[str] = []
    weak_hypotheses: list[str] = []
    cross_checks: list[str] = []
    theme_analyses: list[ThemeAnalysis] = []
    safety_note: str | None = None


class AnalysisOptions(BaseModel):
    themes: list[str] = []
    include_followup_questions: bool = True
    include_markdown_report: bool = True


class AnalysisRequest(BaseModel):
    birth: dict
    options: AnalysisOptions = AnalysisOptions()


class AnalysisResponse(BaseModel):
    chart: dict
    analysis: AnalysisResult
    followup_questions: list[FollowupQuestion] = []
    report_markdown: str | None = None


class ErrorResponse(BaseModel):
    error: dict
