---
title: 'Artifact models and atomic IO'
type: 'feature'
ticket: '4'
created: '2026-09-30'
status: 'built'
baseline_revision: '5fbf875b13f47a3013197ef6dbdc9841cfdec2b3'
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

**Problem:** Stages will pass data only through artifacts (AD-1, AD-3). A crash mid-write must never leave a file that looks complete (AD-10), and a corrupt artifact must stop the run rather than be trusted (AD-9). Nothing defines the shared artifact shape or how artifacts are written and read.

**Approach:** Add the artifact base model and the Issue model in `preloot/models/artifacts.py`, and the only artifact read/write functions in `preloot/io`. A write goes to a temp file, is read back and validated against its model, then renamed into place. A read that fails its model raises one environment error type.

## Boundaries & Constraints

**Always:**
- `Artifact` (pydantic) has `schema_version: int`, `run_id: str`, `issues: list[Issue]` (default empty, AD-9). Each subclass declares its current version as the field default. Reading a file whose `schema_version` differs from the model's default is an environment error.
- `Issue` is frozen, with `stage`, `kind`, `subject`, `detail` (all `str`).
- Artifacts are write-once. `write_artifact` refuses an existing target with an environment error. It never overwrites.
- Writes use UTF-8 JSON, `indent=2`, with the temp file at `<name>.tmp` beside the target. The temp file is flushed and fsynced, re-validated from disk, then moved with `os.replace`. If validation fails, the temp file is deleted and the target never appears.
- One exception type, `ArtifactError(RuntimeError)`, carries the path and the cause.

**Never:**
- Don't edit `src/preloot/models/__init__.py`, `cli.py`, or `models/settings.py`. Entry 6 moves settings onto this IO.
- No stage runner, skip logic, or temp cleanup on start (entry 7). No HTTP (epic-contested-items).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Round trip | Write a subclass instance, then read it back | Equal model; file is indented UTF-8 JSON | No error expected |
| Killed before rename | `os.replace` raises during the write | Target absent | Exception propagates as `ArtifactError` |
| Target exists | Write to an existing path | Existing file byte-for-byte unchanged | `ArtifactError` names the path |
| Invalid JSON | Read a truncated file | — | `ArtifactError` |
| Model mismatch | Read JSON missing a required field | — | `ArtifactError` |
| Old schema | Read `schema_version` different from model default | — | `ArtifactError` stating expected vs found |
| Missing file | Read a path that doesn't exist | — | `FileNotFoundError` (the stage runner checks existence) |
| Issues default | Subclass built without issues | `issues == []`, round-trips | No error expected |

</frozen-after-approval>

## Code Map

- `src/preloot/models/` -- has an empty `__init__.py` (never edit it), plus `settings.py` (plain `BaseModel`, not an artifact yet), `wowsims.py` and `phases.py`. Add `artifacts.py` as a sibling.
- `src/preloot/io/` -- doesn't exist yet. Create the package with an empty `__init__.py` and put the functions in `io/artifacts.py`. Import as `from preloot.io.artifacts import ...`; stdlib `io` is unaffected by the absolute imports.
- `tests/` -- pytest with `tmp_path` and `monkeypatch`, as in `tests/test_cli.py`. pydantic 2.13.5.

## Tasks & Acceptance

**Execution:**
- [ ] `src/preloot/models/artifacts.py` -- `Issue` (frozen) and `Artifact(BaseModel)` per Always. -- Shared shapes for AD-3 and AD-9.
- [ ] `src/preloot/io/__init__.py` -- Empty. -- Package marker.
- [ ] `src/preloot/io/artifacts.py` -- `ArtifactError`, `write_artifact(path: Path, artifact: Artifact) -> None`, `read_artifact(path: Path, model: type[A]) -> A` per Always. -- The only artifact IO (AD-1).
- [ ] `tests/test_artifacts.py` -- One test per matrix row, using a small `Artifact` subclass defined in the test file. -- Matrix coverage.

**Acceptance Criteria:**
- Given any failure between the temp write and the rename, when the target path is checked, then it doesn't exist.
- Given a written artifact, when the file is opened, then it holds `schema_version`, `run_id` and `issues` keys.

## Implementation Notes

- The implementer delivered the models, IO and matrix tests (41 passed). It skipped the `io/__init__.py` task, and it created an unplanned `ProjectState.md`, which the orchestrator deleted as out of scope.
- Base `Artifact.schema_version` defaults to 1, and subclasses override the default. `read_artifact` compares against the model's default.
- Review patches were applied by the orchestrator because the implementer could not be re-engaged. Final suite: 42 passed.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick lens): 2 findings plus 1 found by the orchestrator while verifying. Verdicts: high 0, medium 0, low 3, false 0, maybe-false 0.
  - low / patch — `src/preloot/io/__init__.py` was missing despite the plan task. Imports worked only as an implicit namespace package. Added the empty file.
  - low / patch — `src/preloot/io/artifacts.py`: an unreachable `except ArtifactError: raise` in `write_artifact`. Deleted.
  - low / patch (orchestrator) — `read_artifact` raised a raw `UnicodeDecodeError` for a non-UTF-8 file, breaking the single-`ArtifactError` rule. It is now wrapped, and `test_read_non_utf8_raises_artifact_error` was added.

## Verification

**Commands:**
- `uv run pytest -q` -- expected: all tests pass, exit 0
