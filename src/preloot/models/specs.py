from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    DPS = "dps"
    HEALER = "healer"
    TANK = "tank"


class UnknownSpecError(ValueError):
    pass


@dataclass(frozen=True)
class Spec:
    id: str
    class_name: str
    role: Role


# One row per TBC talent spec with a wowtbc.gg BiS page (verified 2026-09-30).
SPECS: tuple[Spec, ...] = (
    Spec("balance_druid", "druid", Role.DPS),
    Spec("feral_dps_druid", "druid", Role.DPS),
    Spec("feral_tank_druid", "druid", Role.TANK),
    Spec("restoration_druid", "druid", Role.HEALER),
    Spec("beast_mastery_hunter", "hunter", Role.DPS),
    Spec("marksmanship_hunter", "hunter", Role.DPS),
    Spec("survival_hunter", "hunter", Role.DPS),
    Spec("arcane_mage", "mage", Role.DPS),
    Spec("fire_mage", "mage", Role.DPS),
    Spec("frost_mage", "mage", Role.DPS),
    Spec("holy_paladin", "paladin", Role.HEALER),
    Spec("protection_paladin", "paladin", Role.TANK),
    Spec("retribution_paladin", "paladin", Role.DPS),
    Spec("holy_priest", "priest", Role.HEALER),
    Spec("shadow_priest", "priest", Role.DPS),
    Spec("assassination_rogue", "rogue", Role.DPS),
    Spec("combat_rogue", "rogue", Role.DPS),
    Spec("subtlety_rogue", "rogue", Role.DPS),
    Spec("elemental_shaman", "shaman", Role.DPS),
    Spec("enhancement_shaman", "shaman", Role.DPS),
    Spec("restoration_shaman", "shaman", Role.HEALER),
    Spec("affliction_warlock", "warlock", Role.DPS),
    Spec("demonology_warlock", "warlock", Role.DPS),
    Spec("destruction_warlock", "warlock", Role.DPS),
    Spec("destruction_fire_warlock", "warlock", Role.DPS),
    Spec("arms_warrior", "warrior", Role.DPS),
    Spec("fury_warrior", "warrior", Role.DPS),
    Spec("protection_warrior", "warrior", Role.TANK),
)

SPEC_IDS: tuple[str, ...] = tuple(spec.id for spec in SPECS)

_BY_ID = {spec.id: spec for spec in SPECS}


def get_spec(spec_id: str) -> Spec:
    try:
        return _BY_ID[spec_id]
    except KeyError:
        raise UnknownSpecError(
            f"unknown spec {spec_id!r}; valid specs: {', '.join(SPEC_IDS)}"
        ) from None


def specs_by_role(role: Role) -> tuple[Spec, ...]:
    return tuple(spec for spec in SPECS if spec.role is role)
