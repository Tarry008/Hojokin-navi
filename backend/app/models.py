from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

Level = Literal["high", "medium", "low"]


class Evidence(BaseModel):
    page: int
    source_url: str
    snippet: str


class Reason(BaseModel):
    text: str
    evidence_ref: int


class TodoItem(BaseModel):
    text: str
    evidence_ref: int


class Deadline(BaseModel):
    date: Optional[str]
    evidence_ref: Optional[int]


class ProgramRecommendation(BaseModel):
    program_id: str
    program_name: str
    eligible: bool
    level: Level
    reasons: List[Reason]
    deadline: Deadline
    todo: List[TodoItem]
    evidence: List[Evidence]


class RecommendationResponse(BaseModel):
    municipality: str
    results: List[ProgramRecommendation]
    meta: dict


class UserInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    age: int
    income_yen: int
    household: int
    occupation: str
    gender: Optional[str] = None
    dependents: Optional[int] = None
    municipality: Optional[str] = None
    user_id: Optional[str] = None


class Eligibility(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    income_min_yen: Optional[int] = None
    income_max_yen: Optional[int] = None
    household_min: Optional[int] = None
    household_max: Optional[int] = None
    dependents_min: Optional[int] = None
    dependents_max: Optional[int] = None
    gender_keywords: Optional[List[str]] = None
    occupation_keywords: Optional[List[str]] = None
    notes: Optional[str] = None


class Program(BaseModel):
    program_id: str
    program_name: str
    municipality: str
    summary: str
    eligibility: Eligibility
    deadline: Optional[str] = None
    gray_zone_guidance: List[str] = Field(default_factory=list)


class LLMBatchProgramFormat(BaseModel):
    program_id: str
    reasons: List[Reason]
    deadline: Deadline
    todo: List[TodoItem]
    evidence: List[Evidence]


class LLMBatchFormat(BaseModel):
    results: List[LLMBatchProgramFormat]
