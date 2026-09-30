---
title: 'Tracer: scaffold, CLI and one-folder build'
type: 'feature'
ticket: '1'
created: '2026-09-30'
status: 'built'
baseline_revision: 'NO_VCS'
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

**Problem:** PreLoot has no code. Nothing yet proves that a Python 3.14 command line can be frozen into a PyInstaller one-folder build that writes into a workspace run folder.

**Approach:** Scaffold the uv project and the smallest `preloot run --workspace <dir> --phase <id>` path that writes `runs/<phase>/<run_id>/settings.json` from a settings model. Then build it with a PyInstaller one-folder spec into `dist/preloot/preloot.exe`, proving every layer connects.

## Boundaries & Constraints

**Always:**
- Use the src layout `src/preloot/`, Python `>=3.14,<3.15`, pydantic `2.13.5`, and dev dependencies `pytest` and `pyinstaller==6.22.3`.
- `src/preloot/models/__init__.py` is empty and stays empty. Later stories add sibling modules and never edit it.
- The settings model lives in `src/preloot/models/settings.py` and holds only `target_phase` (str). Entry 6 extends it.
- `run_id` is a UTC timestamp `YYYYMMDDTHHMMSSZ`.
- The command line uses stdlib `argparse` with subcommands. `run` is the only one; entry 2 adds `version`.
- The command line creates the workspace and run folders if they are missing, and writes nothing outside `<workspace>`.

**Never:**
- No Phase validation or Previous Phase derivation (entries 3 and 6), and no resume or run reuse (entry 6).
- No atomic write helper or artifact base model (entry 4), no stage runner or `run.log` (entry 7), and no `wowsimcli.exe` bundling or `version` command (entry 2).
- No third-party CLI framework. No one-file PyInstaller mode (architecture AD-12).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Happy path | `run --workspace W --phase p4`, W missing | Creates `W/runs/p4/<run_id>/settings.json` = `{"target_phase": "p4"}`; prints its path; exit 0 | No error expected |
| Existing workspace | W exists with other runs | New `<run_id>` folder; existing runs untouched | No error expected |
| Missing argument | `run --phase p4` (no workspace) | argparse usage message on stderr | Exit 2 |
| No subcommand | `preloot` alone | Usage message | Exit 2 |

</frozen-after-approval>

## Code Map

- Repo root `C:/Repos/preloot-agent` -- greenfield. There's no `pyproject.toml`. Existing folders `.agents/`, `_bmad/`, `_bmad-output/` and `skills-lock.json` must not change.
- `_bmad/scripts/*.py` -- BMad tooling. It uses PEP 723 inline script metadata, so a root `pyproject.toml` doesn't affect `uv run` of these scripts.
- `.venv/` -- empty Python 3.14.2 venv made by pip. uv may adopt it as the project environment through `uv sync`.
- Network -- uv already downloaded pydantic 2.13.5 and PyInstaller 6.22.3 through the corporate proxy (verified 2026-09-30).
- Architecture Structural Seed -- `src/preloot/{cli.py, models/, io/, stages/, templates/}`, `vendor/wowsims/`, `preloot.spec`. This story creates only `cli.py`, `models/`, and `preloot.spec`.

## Tasks & Acceptance

**Execution:**
- [ ] `pyproject.toml`, `.python-version`, `.gitignore` -- Scaffold with `uv init --package --name preloot` (its current default build backend). Then set `requires-python`, pin `pydantic==2.13.5`, add dev group `pytest` and `pyinstaller==6.22.3`, set the script `preloot = "preloot.cli:main"`, and ignore `dist/`, `build/`, `.venv/`. Delete any sample code `uv init` generates that this plan doesn't use. -- The generated defaults come from the tool, not hand-rolled.
- [ ] `src/preloot/__init__.py` -- `__version__ = "0.1.0"`. -- Entry 2 prints it.
- [ ] `src/preloot/models/__init__.py` -- Empty. -- Shared package; later modules are siblings.
- [ ] `src/preloot/models/settings.py` -- pydantic `Settings` with `target_phase: str`. -- The settings contract that entry 6 extends.
- [ ] `src/preloot/cli.py` -- `main(argv: list[str] | None = None) -> int` with an argparse `run` subcommand. Makes the run folder, writes `settings.json` via `Settings.model_dump_json(indent=2)` in UTF-8, prints the path, returns 0. -- Tracer path.
- [ ] `src/preloot/__main__.py` -- Calls `sys.exit(main())`. -- `python -m preloot` and the PyInstaller entry.
- [ ] `preloot.spec` -- One-folder spec: `Analysis(['src/preloot/__main__.py'], pathex=['src'])`, then `EXE(name='preloot', console=True, exclude_binaries=True)` and `COLLECT(name='preloot')`. -- Produces `dist/preloot/preloot.exe`.
- [ ] `tests/test_cli.py` -- Cover every I/O matrix row by calling `main([...])` with `tmp_path`. -- Unit coverage of the tracer.

**Acceptance Criteria:**
- Given a fresh clone, when `uv sync` then `uv run pytest` runs, then all tests pass.
- Given the built bundle, when `dist\preloot\preloot.exe run --workspace <tmp> --phase p4` runs on the dev PC, then `<tmp>\runs\p4\<run_id>\settings.json` exists and its `target_phase` is `p4`.
- Given the repo before and after, when the story is done, then `.agents/`, `_bmad/`, `_bmad-output/` and `skills-lock.json` are unchanged.

## Implementation Notes

- The implementer scaffolded with `uv init --package`, which uses the `uv_build` backend and generated an empty `README.md`. The build emits a PyInstaller warning, "hidden import tzdata not found". It doesn't affect this path.
- Orchestrator fix before review: added `[tool.pytest.ini_options] testpaths = ["tests"]`. Without it, `uv run pytest` at the repo root collected `_bmad/scripts/tests` and failed on an unrelated import. `uv run pytest -q` now gives 4 passed, exit 0.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick lens): 0 findings. Verdict counts: high 0, medium 0, low 0, false 0, maybe-false 0.
- Orchestrator self-check (not a lens finding), verdict `false`: two runs in the same UTC second share a `run_id` and rewrite `settings.json`. The run folder is keyed by phase, and the settings hold only `target_phase`, so the rewritten content is identical. Entry 6 defines identical settings as a resume of the same run.

## Verification

**Commands:**
- `uv sync` -- expected: environment created, no errors
- `uv run pytest -q` -- expected: all tests pass
- `uv run pyinstaller preloot.spec --noconfirm` -- expected: `dist/preloot/preloot.exe` exists
- `.\dist\preloot\preloot.exe run --workspace $env:TEMP\preloot-tracer --phase p4` -- expected: exit 0 and prints a path to a `settings.json` containing `"target_phase": "p4"`
