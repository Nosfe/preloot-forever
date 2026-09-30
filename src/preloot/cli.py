from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from preloot.models.settings import Settings


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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="preloot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--workspace", required=True)
    run_parser.add_argument("--phase", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(Path(args.workspace), args.phase)

    return 0
