from __future__ import annotations

try:
    from pydantic import BaseModel, Field
except ImportError:  # fallback for environments without package install access
    from dataclasses import dataclass, field

    def Field(default_factory=list):  # type: ignore
        return field(default_factory=default_factory)

    class BaseModel:
        def model_dump(self) -> dict:
            return self.__dict__.copy()

    def _dataclass(cls):
        return dataclass(cls)
else:
    def _dataclass(cls):
        return cls


@_dataclass
class SourceItem(BaseModel):
    source_id: str
    title: str
    text: str


@_dataclass
class ExtractedComplaint(BaseModel):
    source_id: str
    sentence: str
    severity_hints: int = 0
    buying_hints: int = 0


@_dataclass
class ComplaintTheme(BaseModel):
    theme_id: str
    label: str
    complaint_count: int
    evidence: list[str] = Field(default_factory=list)
    severity_score: int = 0
    buying_signal_score: int = 0


@_dataclass
class RankedTheme(BaseModel):
    theme_id: str
    label: str
    complaint_count: int
    severity_score: int
    buying_signal_score: int
    importance_score: float
    evidence: list[str] = Field(default_factory=list)


@_dataclass
class PipelineResult(BaseModel):
    niche: str
    source_count: int
    extracted_count: int
    ranked_themes: list[RankedTheme]