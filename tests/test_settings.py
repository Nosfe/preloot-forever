from __future__ import annotations

from preloot.models.settings import Settings
from preloot.models.wowsims import WOWSIMS_VERSION


def test_settings_defaults_match_contract() -> None:
    settings = Settings(run_id="20260930T120000Z", target_phase="p4", previous_phase="p3")

    assert settings.schema_version == 1
    assert settings.issues == []
    assert settings.encounter.duration_seconds == 180
    assert settings.encounter.duration_variation_seconds == 5
    assert settings.encounter.targets == 1
    assert settings.iterations == 12500
    assert settings.seed == 1
    assert settings.wowsims_version == WOWSIMS_VERSION
    assert settings.source_urls.wowtbc_bis_page_data == "https://wowtbc.gg/page-data/bis-list/{slug}/page-data.json"
    assert (
        settings.source_urls.wowsims_db
        == f"https://raw.githubusercontent.com/wowsims/tbc-new/{WOWSIMS_VERSION}/assets/database/db.json"
    )
