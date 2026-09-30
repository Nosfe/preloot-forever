from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from preloot import __version__
from preloot.models.settings import Settings
from preloot.models.wowsims import WOWSIMS_VERSION
from preloot.wowsimcli import WowsimcliError, bundled_version


def _utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_command(workspace: Path, phase: str) -> int:
    run_dir = workspace / "runs" / phase / _utc_run_id()
    run_dir.mkdir(parents=True, exist_ok=True)

    settings = Settings(target_phase=phase)
    settings_path = run_dir / "settings.json"
    settings_path.write_text(settings.model_dump_json(indent=2), encoding="utf-8")

    print(settings_path)
    return 0


def _version_command() -> int:
    try:
        current = bundled_version()
    except WowsimcliError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if current != WOWSIMS_VERSION:
        print(
            f"wowsimcli version mismatch: expected {WOWSIMS_VERSION}, found {current}",
            file=sys.stderr,
        )
        return 1

    print(f"preloot {__version__}")
    print(f"wowsimcli {current}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="preloot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--workspace", required=True)
    run_parser.add_argument("--phase", required=True)

    subparsers.add_parser("version")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(Path(args.workspace), args.phase)

    if args.command == "version":
        return _version_command()

    return 0
