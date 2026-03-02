from pydantic import BaseModel, Field
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "crtical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Finding(BaseModel):
    file: str = Field(description="File path where the issue was found")
    line: int | None = Field(default=None, description="Line number if applicable")
    title: str = Field(description="Short summary of the finding")
    description: str = Field(description="Detailed explanation of the finding")
    severity: Severity=Field(description="Severity level of the finding")
    recommendation: str = Field(description="Recommended fix or improvement for the finding")

class AgentReport(BaseModel):
    agent_name: str
    summary: str = Field(description="Brief overall summary")
    findings: list[Finding] = Field(default_factory=list)
    score: int = Field(ge=0, le=100, description="Overall score out of 100")

class ReviewReport(BaseModel):
    repo_name: str
    files_reviewed: int
    security: AgentReport
    quality: AgentReport
    performance: AgentReport
    documentation: AgentReport
    overall_score: int = Field(ge=0, le=100)
    summary: str = Field(description="Consolidated review summary")