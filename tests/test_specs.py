from __future__ import annotations

import pytest

from preloot.models.specs import SPEC_IDS, SPECS, Role, UnknownSpecError, get_spec, specs_by_role

CLASSES = {"druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior"}


def test_table_lists_the_28_wowtbc_gg_specs() -> None:
    assert len(SPECS) == 28
    assert len(set(SPEC_IDS)) == 28


def test_each_spec_has_one_known_class_and_one_role() -> None:
    for spec in SPECS:
        assert spec.class_name in CLASSES
        assert isinstance(spec.role, Role)
        assert spec.id.endswith(f"_{spec.class_name}")


def test_role_counts() -> None:
    assert len(specs_by_role(Role.DPS)) == 21
    assert {s.id for s in specs_by_role(Role.HEALER)} == {
        "holy_paladin",
        "holy_priest",
        "restoration_druid",
        "restoration_shaman",
    }
    assert {s.id for s in specs_by_role(Role.TANK)} == {
        "feral_tank_druid",
        "protection_paladin",
        "protection_warrior",
    }


def test_talent_specs_sharing_a_wowsims_spec_stay_distinct() -> None:
    assert get_spec("fury_warrior") != get_spec("arms_warrior")
    assert get_spec("fury_warrior").role is get_spec("arms_warrior").role is Role.DPS


def test_unknown_spec_names_valid_ids() -> None:
    with pytest.raises(UnknownSpecError, match="valid specs: balance_druid"):
        get_spec("discipline_priest")
