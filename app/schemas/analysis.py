from pydantic import BaseModel, Field

from app.schemas.birth import BirthInfo


class ThemeAnalysis(BaseModel):
    theme: str
    observations: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    uncertainty: str | None = None
    followup_questions: list[str] = Field(default_factory=list)


class FollowupQuestion(BaseModel):
    question: str
    reason: str
    related_chart_factors: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    summary: str
    strong_signals: list[str] = Field(default_factory=list)
    weak_hypotheses: list[str] = Field(default_factory=list)
    cross_checks: list[str] = Field(default_factory=list)
    theme_analyses: list[ThemeAnalysis] = Field(default_factory=list)
    safety_note: str | None = None


class AnalysisOptions(BaseModel):
    themes: list[str] = Field(default_factory=list)
    include_followup_questions: bool = True
    include_markdown_report: bool = True


class AnalysisRequest(BaseModel):
    birth: BirthInfo
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


class AnalysisResponse(BaseModel):
    chart: dict
    analysis: AnalysisResult
    followup_questions: list[FollowupQuestion] = Field(default_factory=list)
    report_markdown: str | None = None


class ErrorResponse(BaseModel):
    error: dict
