---
type: epic
title: "PreLoot runs from a portable folder"
parent: initiative-preloot
covers: [CAP-1, CAP-9, CAP-10]
after: []
assignee: ""
risk: medium
---

# PreLoot runs from a portable folder

## Description

The platform baseline: a PyInstaller one-folder build of PreLoot, with `wowsimcli.exe` v0.0.145 bundled, that runs on a Windows 11 PC with no Python installed. It covers the command line, target-phase selection, run settings, run folders with resume, and the shared code every later epic builds on: `preloot.models`, `preloot.io`, and the stage runner. It covers only the run-folder part of CAP-9; resuming the sim results belongs to epic-sim-priority.

## Outcome

The officer can copy one zip to the personal PC and start a PreLoot run for a Target Phase. It is the base the spec's success signal depends on.

## Requirements

- R1 (CAP-10): A PyInstaller one-folder build of PreLoot, with `wowsimcli.exe` v0.0.145 bundled, runs on Windows 11 x64 with no Python, and the bundle is never written to. (architecture AD-11, AD-12)
- R2 (CAP-1): `preloot run --workspace <dir> --phase <id>` accepts a canonical Phase ID and derives the Previous Phase from the Phase table. (architecture AD-14)
- R3 (CAP-9): The CLI writes `settings.json` once per run in `runs/<target_phase>/<run_id>/`, with Target and Previous Phase, encounter, iterations, seed, wowsims version and source URLs. Identical settings resume the latest run; any change starts a new `run_id`. (architecture AD-10)
- R4 (CAP-9): An artifact is written to a temp file and renamed only after model validation. A stage whose artifact exists is skipped. An artifact that fails its model is an environment failure. (architecture AD-9, AD-10)
- R5 (CAP-9): The artifact base model carries `schema_version` and `run_id`; the Issue model is `{stage, kind, subject, detail}`. (architecture AD-3, AD-9)
- R6 (CAP-1): The Spec table lists every TBC talent Spec with its PreLoot ID, class and Role, Tanks included as Role Tank. Later epics add the wowtbc.gg page names and the wowsims spec and talent build. (architecture AD-4)
- R7 (CAP-9): Each run writes a plain-text `run.log` with per-stage progress. (architecture, Consistency Conventions)

## Done when

1. The zip built on the dev PC is unzipped on a Windows 11 PC with no Python, and runs `preloot run --workspace <dir> --phase p4`.
2. The run writes `runs/p4/<run_id>/settings.json` with Target Phase P4, Previous Phase P3, the encounter, iterations, seed, and wowsims v0.0.145.
3. A rerun with identical settings resumes the same `run_id`, and any changed setting starts a new one.
4. After a run, the bundle folder is byte-for-byte unchanged, and the bundled `wowsimcli.exe` starts from it.
5. The Spec table in `preloot.models` lists every DPS and Healer Spec with its class and Role, and the Phase table maps every Phase per AD-14.

## Boundaries

Packaging, the command line, the run folder, and shared models and IO. No source fetching and no sims. The Spec table is created here with Spec, class and Role; epic-contested-items adds the wowtbc.gg page names and epic-sim-priority adds the wowsims spec and talent build.

## References

- spec — _bmad-output/initiative-preloot/spec-preloot/spec-preloot.md, CAP-1, CAP-9, CAP-10
- spec — _bmad-output/initiative-preloot/spec-preloot/acceptance-criteria.md, sections CAP-1, CAP-9, CAP-10
- architecture — _bmad-output/initiative-preloot/architecture-preloot/architecture-preloot.md, AD-1, AD-3, AD-4, AD-9, AD-10, AD-11, AD-12, AD-14, Stack, Structural Seed

## Notes

- Assumption: a person runs the zip on the personal PC to check Done when 1 and 4; that step is hitl (entry 9).
- Decision: tracer bullet is entry 1 — the scaffold, CLI, minimal settings and one-folder build prove every layer connects (2026-09-30).
- Decision: entries 2, 3, 4 and 5 run in parallel after entry 1. Each owns its own module in `preloot.models` (`wowsims.py`, `phases.py`, `artifacts.py`, `specs.py`), and none edits `cli.py`; entry 6 wires the CLI (2026-09-30).
- Decision: `run_id` is a UTC timestamp, and a run resumes when every setting but `run_id` matches the latest run (2026-09-30).
- Decision: the default iteration count is the wowsims default (user's decision, 2026-09-30).
- Decision: HTTP with truststore and Warcraft Logs secrets loading are not in this epic; their earliest users, epic-contested-items and epic-sim-priority, own them (2026-09-30).
- Decision: refactor sweep is entry 8, and the portable run on the personal PC is entry 9, after it (2026-09-30).
