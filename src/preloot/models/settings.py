from __future__ import annotations

from pydantic import BaseModel, Field

from preloot.models.artifacts import Artifact
from preloot.models.wowsims import WOWSIMS_VERSION


class Encounter(BaseModel):
    duration_seconds: int = 180
    duration_variation_seconds: int = 5
    targets: int = 1


class SourceUrls(BaseModel):
    wowtbc_bis_page_data: str = "https://wowtbc.gg/page-data/bis-list/{slug}/page-data.json"
    wowsims_db: str = f"https://raw.githubusercontent.com/wowsims/tbc-new/{WOWSIMS_VERSION}/assets/database/db.json"


class Settings(Artifact):
    target_phase: str
    previous_phase: str
    encounter: Encounter = Field(default_factory=Encounter)
    iterations: int = 12500
    seed: int = 1
    wowsims_version: str = WOWSIMS_VERSION
    source_urls: SourceUrls = Field(default_factory=SourceUrls)
