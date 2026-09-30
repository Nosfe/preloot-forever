from __future__ import annotations

import pytest

from preloot.models.phases import (
    PHASE_IDS,
    NoPreviousPhaseError,
    UnknownPhaseError,
    from_wowsims_phase,
    from_wowtbc_flag,
    get_phase,
    previous_phase,
)

GLOSSARY = [
    ("pre", "pre-raid", "pre-bis", None),
    ("p1", "P1", "t4", 1),
    ("p2", "P2", "t5", 2),
    ("p3", "P3", "t6", 3),
    ("p4", "P4", "za", 4),
    ("p5", "P5", "swp", 5),
]


def test_phase_ids_are_in_release_order() -> None:
    assert PHASE_IDS == ("pre", "p1", "p2", "p3", "p4", "p5")


@pytest.mark.parametrize(("phase_id", "label", "flag", "number"), GLOSSARY)
def test_each_phase_matches_the_glossary(phase_id: str, label: str, flag: str, number: int | None) -> None:
    phase = get_phase(phase_id)

    assert (phase.label, phase.wowtbc_flag, phase.wowsims_phase) == (label, flag, number)
    assert from_wowtbc_flag(flag) is phase
    if number is not None:
        assert from_wowsims_phase(number) is phase


@pytest.mark.parametrize(
    ("target", "previous"),
    [("p1", "pre"), ("p2", "p1"), ("p3", "p2"), ("p4", "p3"), ("p5", "p4")],
)
def test_previous_phase(target: str, previous: str) -> None:
    assert previous_phase(target).id == previous


def test_pre_has_no_previous_phase() -> None:
    with pytest.raises(NoPreviousPhaseError):
        previous_phase("pre")


def test_unknown_phase_names_valid_ids() -> None:
    with pytest.raises(UnknownPhaseError, match="valid phases: pre, p1, p2, p3, p4, p5"):
        get_phase("p9")


def test_unknown_phase_in_previous_phase() -> None:
    with pytest.raises(UnknownPhaseError):
        previous_phase("p9")


def test_unknown_source_names_raise() -> None:
    with pytest.raises(UnknownPhaseError):
        from_wowtbc_flag("t7")
    with pytest.raises(UnknownPhaseError):
        from_wowsims_phase(6)
