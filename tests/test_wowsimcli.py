from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

import pytest

from preloot.wowsimcli import WowsimcliError, bundled_version, locate


def test_locate_source_tree(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("preloot.wowsimcli._repo_root", lambda: tmp_path)
    monkeypatch.setattr("preloot.wowsimcli.sys", type("S", (), {"frozen": False})())

    path = locate()

    assert path == tmp_path / "vendor" / "wowsims" / "wowsimcli.exe"


def test_locate_frozen_bundle(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_sys = type("S", (), {"frozen": True, "_MEIPASS": str(tmp_path)})()
    monkeypatch.setattr("preloot.wowsimcli.sys", fake_sys)

    path = locate()

    assert path == tmp_path / "wowsims" / "wowsimcli.exe"


def test_bundled_version_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    exe_path = tmp_path / "wowsimcli.exe"
    exe_path.write_bytes(b"binary")
    monkeypatch.setattr("preloot.wowsimcli.locate", lambda: exe_path)
    monkeypatch.setattr(
        "preloot.wowsimcli.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args=args[0], returncode=0, stdout="v0.0.145\n", stderr=""),
    )

    assert bundled_version() == "v0.0.145"


def test_bundled_version_missing_binary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    exe_path = tmp_path / "missing.exe"
    monkeypatch.setattr("preloot.wowsimcli.locate", lambda: exe_path)

    with pytest.raises(WowsimcliError, match="expected path"):
        bundled_version()


def test_bundled_version_nonzero_exit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    exe_path = tmp_path / "wowsimcli.exe"
    exe_path.write_bytes(b"binary")
    monkeypatch.setattr("preloot.wowsimcli.locate", lambda: exe_path)
    monkeypatch.setattr(
        "preloot.wowsimcli.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args=args[0], returncode=1, stdout="", stderr="failed"),
    )

    with pytest.raises(WowsimcliError, match="failed"):
        bundled_version()
