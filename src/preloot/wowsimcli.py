from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class WowsimcliError(RuntimeError):
    pass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def locate() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS"))
        return base / "wowsims" / "wowsimcli.exe"

    return _repo_root() / "vendor" / "wowsims" / "wowsimcli.exe"


def bundled_version() -> str:
    binary_path = locate()
    if not binary_path.exists():
        raise WowsimcliError(f"wowsimcli not found at expected path: {binary_path}")

    try:
        result = subprocess.run(
            [str(binary_path), "version"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise WowsimcliError(f"failed to run wowsimcli at {binary_path}: {exc}") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        if detail:
            raise WowsimcliError(
                f"wowsimcli version command failed at {binary_path}: {detail}"
            )
        raise WowsimcliError(
            f"wowsimcli version command failed at {binary_path} with exit code {result.returncode}"
        )

    version = result.stdout.strip()
    if not version:
        raise WowsimcliError(
            f"wowsimcli version command returned empty output at {binary_path}"
        )

    return version
