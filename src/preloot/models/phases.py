from __future__ import annotations

from dataclasses import dataclass


class UnknownPhaseError(ValueError):
    pass


class NoPreviousPhaseError(ValueError):
    pass


@dataclass(frozen=True)
class Phase:
    id: str
    label: str
    wowtbc_flag: str
    wowsims_phase: int | None


PHASES: tuple[Phase, ...] = (
    Phase("pre", "pre-raid", "pre-bis", None),
    Phase("p1", "P1", "t4", 1),
    Phase("p2", "P2", "t5", 2),
    Phase("p3", "P3", "t6", 3),
    Phase("p4", "P4", "za", 4),
    Phase("p5", "P5", "swp", 5),
)

PHASE_IDS: tuple[str, ...] = tuple(phase.id for phase in PHASES)

_BY_ID = {phase.id: phase for phase in PHASES}
_BY_WOWTBC_FLAG = {phase.wowtbc_flag: phase for phase in PHASES}
_BY_WOWSIMS_PHASE = {phase.wowsims_phase: phase for phase in PHASES if phase.wowsims_phase is not None}


def get_phase(phase_id: str) -> Phase:
    try:
        return _BY_ID[phase_id]
    except KeyError:
        raise UnknownPhaseError(
            f"unknown phase {phase_id!r}; valid phases: {', '.join(PHASE_IDS)}"
        ) from None


def from_wowtbc_flag(flag: str) -> Phase:
    try:
        return _BY_WOWTBC_FLAG[flag]
    except KeyError:
        raise UnknownPhaseError(f"unknown wowtbc.gg phase flag {flag!r}") from None


def from_wowsims_phase(number: int) -> Phase:
    try:
        return _BY_WOWSIMS_PHASE[number]
    except KeyError:
        raise UnknownPhaseError(f"unknown wowsims phase {number!r}") from None


def previous_phase(phase_id: str) -> Phase:
    index = PHASES.index(get_phase(phase_id))
    if index == 0:
        raise NoPreviousPhaseError(f"phase {phase_id!r} has no previous phase")
    return PHASES[index - 1]
