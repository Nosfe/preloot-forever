from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Issue(BaseModel):
    model_config = ConfigDict(frozen=True)

    stage: str
    kind: str
    subject: str
    detail: str


class Artifact(BaseModel):
    schema_version: int = 1
    run_id: str
    issues: list[Issue] = Field(default_factory=list)
