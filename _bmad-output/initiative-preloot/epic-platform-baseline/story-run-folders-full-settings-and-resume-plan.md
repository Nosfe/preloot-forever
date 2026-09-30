---
title: 'Full run settings and phase validation'
type: 'feature'
ticket: '6'
created: '2026-09-30'
status: 'built'
baseline_revision: '5a59a804eb79564169b8936e1e6d3fa3a6b36e38'
route: 'full'
route_source: 'auto'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-preloot/architecture-preloot/architecture-preloot.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `preloot run` records only the Target Phase and accepts any `--phase`. A run can't say which Phases, sim settings, wowsims version and sources it used (AD-10, AD-14).

**Approach:** Make `settings.json` a full, write-once artifact holding Target and Previous Phase, encounter, iterations, seed, wowsims version and source URLs, written through the artifact IO. Validate `--phase` against the Phase table and add `--seed`. Every call still starts a new run; resume is deferred.

## Boundaries & Constraints

**Always:**
- `Settings` subclasses `Artifact` (`schema_version`, `run_id`, `issues`) and is written only through `write_artifact`.
- Settings fields and defaults:
  - `target_phase` and `previous_phase`: canonical IDs; `previous_phase` comes from `phases.previous_phase`.
  - `encounter`: `{duration_seconds: 180, duration_variation_seconds: 5, targets: 1}` (the wowsims v0.0.145 `ENCOUNTER_DEFAULTS`).
  - `iterations: 12500` (the wowsims v0.0.145 UI default). `seed: 1`.
  - `wowsims_version`: `WOWSIMS_VERSION`.
  - `source_urls`: `wowtbc_bis_page_data = "https://wowtbc.gg/page-data/bis-list/{slug}/page-data.json"` and `wowsims_db = "https://raw.githubusercontent.com/wowsims/tbc-new/{WOWSIMS_VERSION}/assets/database/db.json"`.
- `--phase` accepts only the Phase IDs that have a Previous Phase (`p1`–`p5`), derived from the Phase table. `--seed` is an optional int, default 1.
- Run folder: `<workspace>/runs/<target_phase>/<run_id>/`, where `run_id` is the UTC `YYYYMMDDTHHMMSSZ`. On success, print the path of `settings.json` and exit 0.

**Never:**
- No resume or run reuse (deferred). Don't edit `src/preloot/models/__init__.py`. No stage runner or `run.log` (entry 7). No Warcraft Logs URL. No `--iterations` flag.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| New run | `run --workspace W --phase p4` | `W/runs/p4/<id>/settings.json` with target p4, previous p3, the defaults, seed 1, v0.0.145; its path printed | No error expected |
| Custom seed | `--phase p4 --seed 7` | Settings seed 7 | No error expected |
| First raid phase | `--phase p1` | previous_phase `pre` | No error expected |
| Unknown phase | `--phase p9` | argparse error listing `p1, p2, p3, p4, p5` | Exit 2 |
| Pre as target | `--phase pre` | Same argparse error | Exit 2 |
| Non-integer seed | `--seed abc` | argparse error | Exit 2 |
| Same-second collision | `<id>` folder already holds `settings.json` | Message naming the path on stderr; existing file unchanged | Exit 1 |

</frozen-after-approval>

## Code Map

- `src/preloot/cli.py` -- `_run_command(workspace, phase)` writes `Settings(target_phase=...)` with `write_text` into `runs/<phase>/<_utc_run_id()>`. Replace that with a `Settings` built from the defaults and `write_artifact`. Catch `ArtifactError` and exit 1. The `version` subcommand stays untouched.
- `src/preloot/models/settings.py` -- `Settings(BaseModel)` with only `target_phase`. Rebase it onto `Artifact` and add nested pydantic `Encounter` and `SourceUrls` in the same file.
- `src/preloot/models/artifacts.py` -- `Artifact(schema_version: int = 1, run_id: str, issues: list[Issue])`.
- `src/preloot/io/artifacts.py` -- `write_artifact(path, artifact)` refuses an existing target with `ArtifactError` and creates parent folders.
- `src/preloot/models/phases.py` -- `PHASES`, `previous_phase` (raises `NoPreviousPhaseError` for `pre`).
- `src/preloot/models/wowsims.py` -- `WOWSIMS_VERSION = "v0.0.145"`.
- `tests/test_cli.py` -- the existing happy-path tests assert the payload `{"target_phase": "p4"}`. Update them to the new contract; keep the missing-argument, no-subcommand and version tests.
- Verified 2026-09-30 at tag v0.0.145: `ENCOUNTER_DEFAULTS = {duration: 180, durationVariation: 5}` (`ui/sim/constants/encounter.ts`), `iterations: 12500` (`ui/sim/state/sim_store.ts`), and the `db.json` tag URL returns 200.

## Tasks & Acceptance

**Execution:**
- [ ] `src/preloot/models/settings.py` -- `Encounter`, `SourceUrls` and `Settings(Artifact)` per Always. -- The single run contract (AD-10).
- [ ] `src/preloot/cli.py` -- `--phase` choices from the Phase table, `--seed`, and settings written via `write_artifact`, per Always and the matrix. -- The CLI alone reads arguments (AD-10).
- [ ] `tests/test_settings.py`, `tests/test_cli.py` -- Cover every matrix row. -- Matrix coverage.

**Acceptance Criteria:**
- Given a new run's `settings.json`, when read with `read_artifact(path, Settings)`, then it validates and its `wowsims_version` equals `WOWSIMS_VERSION`.
- Given the built bundle, when `dist\preloot\preloot.exe run --workspace <tmp> --phase p9` runs, then it exits 2 listing the valid phases.

## Implementation Notes

- Scope was split at the plan gate (about 1,800 tokens). Resume is recorded in `_bmad-output/initiative-preloot/deferred-work.md`. The implementer delivered the narrowed plan: 55 passed, the bundle writes full settings, and `p9` exits 2. The PyInstaller `tzdata` warning is still there and doesn't block anything.
- Orchestrator patch: `RUN_PHASE_CHOICES` is now `PHASES[1:]` (every Phase with a Previous Phase), per the plan, instead of excluding `"pre"` by name.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick lens): 1 finding. Verdicts: high 0, medium 0, low 1, false 0, maybe-false 0.
  - low / patch — `tests/test_settings.py` was indented with 7 spaces (the reviewer said tabs), not the project's 4 spaces. Rewritten with 4-space indentation, and tests are green.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: all tests pass, exit 0
- `uv run python tools/fetch_wowsimcli.py; uv run pyinstaller preloot.spec --noconfirm` -- expected: build completes
- `.\dist\preloot\preloot.exe run --workspace $env:TEMP\preloot-16 --phase p4` -- expected: prints a `settings.json` path; the file names p4, p3, 12500, v0.0.145
- `.\dist\preloot\preloot.exe run --workspace $env:TEMP\preloot-16 --phase p9` -- expected: exit 2 and the list of valid phases
