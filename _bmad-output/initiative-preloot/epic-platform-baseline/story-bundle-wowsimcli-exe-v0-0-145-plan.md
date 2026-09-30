---
title: 'Bundle wowsimcli.exe v0.0.145'
type: 'feature'
ticket: '2'
created: '2026-09-30'
status: 'built'
baseline_revision: 'a1f4cc1e6f5211cdc16e4e54963b9903af4667d3'
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

**Problem:** The one-folder build has no sim engine. Later stages need the exact wowsims `wowsimcli` whose item data PreLoot reads (AD-11). That binary must ship inside the bundle and be found at runtime without Python or a download on the personal PC.

**Approach:** Add a build-time fetch script that downloads the pinned v0.0.145 Windows asset and verifies its sha256. Bundle the binary through the PyInstaller spec, and add a runtime locator plus a `preloot version` command that proves the bundled binary runs and matches the pinned version.

## Boundaries & Constraints

**Always:**
- The pinned version `v0.0.145` is one constant, `WOWSIMS_VERSION`, in `src/preloot/models/wowsims.py`. Entry 6 records it in settings.
- The asset is `https://github.com/wowsims/tbc-new/releases/download/v0.0.145/wowsimcli-windows.exe.zip`, zip sha256 `0fda61b945e0045c25b69854af8017183576ecf3404f1f0bd4bd74d92bc118a1`. It holds `wowsimcli-windows.exe`, which is stored as `vendor/wowsims/wowsimcli.exe`.
- The binary is fetched at build time into `vendor/wowsims/`, which git ignores. It is never committed.
- The bundle places it at `wowsims/wowsimcli.exe` under `sys._MEIPASS`. When running from source it is found at `<repo>/vendor/wowsims/wowsimcli.exe`.
- A missing binary, or a version that differs from `WOWSIMS_VERSION`, is an environment failure: a clear message on stderr and exit code 1 (AD-9, AD-11).
- The fetch script uses stdlib `urllib` with `truststore.inject_into_ssl()`, because the dev PC's corporate proxy breaks Python's default certificate bundle.

**Never:**
- Don't edit `src/preloot/models/__init__.py`, and add nothing to `preloot.io` (entry 4 owns it in parallel).
- No settings changes (entry 6), and no running `sim` (epic-sim-priority).
- No one-file mode. Never extract or run binaries from `%TEMP%`: this dev PC denies running programs there.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fetch, clean | `vendor/wowsims/` empty | Downloads the zip, verifies the sha256, writes `wowsimcli.exe` | No error expected |
| Fetch, already present | Zip present with correct hash | No download; `wowsimcli.exe` re-extracted if missing | No error expected |
| Fetch, bad hash | Downloaded bytes' sha256 ≠ pinned | No zip or exe left behind | Exit 1, message names expected vs actual hash |
| Version, bundled | `preloot version` in build | Prints `preloot 0.1.0` and `wowsimcli v0.0.145`; exit 0 | No error expected |
| Version, source | `preloot version` from repo with vendor exe | Same output | No error expected |
| Binary missing | Locator finds no exe | — | stderr names the expected path; exit 1 |
| Version mismatch | Binary prints another version | — | stderr shows expected vs found; exit 1 |

</frozen-after-approval>

## Code Map

- `src/preloot/cli.py` -- argparse with `subparsers.add_parser("run")` and `main(argv) -> int`. Add a `version` subparser here and reuse the same `main` dispatch.
- `src/preloot/__init__.py` -- `__version__ = "0.1.0"`. Print it; don't duplicate it.
- `preloot.spec` -- `Analysis(["src/preloot/__main__.py"], pathex=["src"])`, then `EXE(exclude_binaries=True)` and `COLLECT(name="preloot")`. Add `binaries=[("vendor/wowsims/wowsimcli.exe", "wowsims")]`, and fail the build with a clear message if the file is missing.
- `.gitignore` -- Has `build/` and `dist/`. Add `vendor/wowsims/`.
- `pyproject.toml` -- Dev group has `pyinstaller==6.22.3` and `pytest`. Add `truststore==0.10.4` to dev (build-time only here; epic-contested-items adds it at runtime).
- Verified 2026-09-30: `wowsimcli version` prints exactly `v0.0.145\n` with exit 0 when called from Python `subprocess.run([...,'version'])` under either filename. `--help` lists `sim`, `version`, `decodelink`.

## Tasks & Acceptance

**Execution:**
- [ ] `src/preloot/models/wowsims.py` -- `WOWSIMS_VERSION = "v0.0.145"`. -- Single pin (AD-11).
- [ ] `src/preloot/wowsimcli.py` -- `locate() -> Path` (frozen: `sys._MEIPASS/wowsims/wowsimcli.exe`; source: repo `vendor/wowsims/wowsimcli.exe`) and `bundled_version() -> str` (runs `version`, strips output). Missing binary or non-zero exit raises a `WowsimcliError` naming the path. -- The only place that knows where the binary lives; `simulate` reuses it later.
- [ ] `src/preloot/cli.py` -- `version` subcommand. It prints `preloot {__version__}` and `wowsimcli {version}`, and returns 1 with a stderr message on `WowsimcliError` or a mismatch with `WOWSIMS_VERSION`. -- Verify command.
- [ ] `tools/fetch_wowsimcli.py` -- Idempotent fetch: verify an existing zip's hash, else download it to `vendor/wowsims/` via urllib + truststore, verify the sha256 (deleting it on mismatch and exiting 1), then extract `wowsimcli-windows.exe` as `wowsimcli.exe`. Builds the URL from `WOWSIMS_VERSION`. -- Build-time step.
- [ ] `preloot.spec`, `.gitignore`, `pyproject.toml` -- Per the Code Map. -- Bundle, ignore, dependency.
- [ ] `tests/test_wowsimcli.py`, `tests/test_fetch_wowsimcli.py` -- Cover every matrix row. Monkeypatch `sys.frozen`/`sys._MEIPASS`, `subprocess.run`, and the download function; no network in tests. -- Matrix coverage.

**Acceptance Criteria:**
- Given `uv run python tools/fetch_wowsimcli.py` then `uv run pyinstaller preloot.spec --noconfirm`, when `dist\preloot\preloot.exe version` runs, then it prints `wowsimcli v0.0.145` and exits 0.
- Given the built bundle, when it is listed, then `wowsimcli.exe` exists under `dist/preloot/_internal/wowsims/`.
- Given `git status` after the build, when it is inspected, then no file under `vendor/` is tracked or staged.

## Implementation Notes

- The implementer delivered every task. Verification: 16 tests passed, fetch and build succeeded, `preloot.exe version` gave `v0.0.145`, and `_internal/wowsims/wowsimcli.exe` is present. The PyInstaller `tzdata` hidden-import warning is still there and doesn't block anything.
- Review patches were applied by the orchestrator because the implementer could not be re-engaged. Tests are now 17 passed and all Verification commands were re-run green.

## Plan Change Log

## Review Triage Log

- Pass 1 (quick lens): 5 findings. Verdicts: high 0, medium 0, low 3, false 2, maybe-false 0.
  - low / patch — `tests/test_cli.py`: the "Version, source" matrix row had no end-to-end test. Added `test_version_command_from_source_tree`, which drives `main(["version"])` through the real `locate()` in source mode.
  - false — `tools/fetch_wowsimcli.py` import of `preloot`: `uv run python tools/fetch_wowsimcli.py` succeeded (the editable project install makes `preloot` importable).
  - false — bundle path unverified: `Test-Path dist/preloot/_internal/wowsims/wowsimcli.exe` returned True after the build.
  - low / rejected — the empty `version` output path is untested. It isn't a matrix row, it's unlikely in everyday use, and the code raises clearly.
  - low / patch — `tests/test_fetch_wowsimcli.py`: the bad-hash test now asserts that both the expected and actual hashes appear in stderr, as the matrix requires.

## Design Notes

The downloaded binary is 24 MB and should not live in git. Pinning its zip hash in the fetch script, together with `WOWSIMS_VERSION`, keeps the build reproducible. The runtime version check keeps the bundle from drifting from the pin.

## Verification

**Commands:**
- `uv sync` -- expected: truststore installed
- `uv run pytest -q` -- expected: all tests pass, exit 0
- `uv run python tools/fetch_wowsimcli.py` -- expected: `vendor/wowsims/wowsimcli.exe` exists; a second run downloads nothing
- `uv run pyinstaller preloot.spec --noconfirm` -- expected: build completes
- `.\dist\preloot\preloot.exe version` -- expected: `preloot 0.1.0` / `wowsimcli v0.0.145`, exit 0
