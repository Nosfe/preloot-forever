from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from preloot.cli import main
from preloot.models.wowsims import WOWSIMS_VERSION
from preloot.wowsimcli import WowsimcliError


def test_happy_path_creates_workspace_and_settings_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"

    code = main(["run", "--workspace", str(workspace), "--phase", "p4"])

    assert code == 0
    settings_path = Path(capsys.readouterr().out.strip())
    assert settings_path.exists()
    assert workspace in settings_path.parents
    assert settings_path.parts[-4:-1] == ("runs", "p4", settings_path.parts[-2])
    assert settings_path.name == "settings.json"

    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    assert payload == {"target_phase": "p4"}


def test_existing_workspace_creates_new_run_without_touching_existing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"
    existing_run = workspace / "runs" / "p4" / "existing-run"
    existing_run.mkdir(parents=True)

    code = main(["run", "--workspace", str(workspace), "--phase", "p4"])

    assert code == 0
    settings_path = Path(capsys.readouterr().out.strip())
    assert settings_path.exists()
    assert existing_run.exists()
    assert settings_path.parent != existing_run


def test_missing_workspace_argument_exits_with_usage(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["run", "--phase", "p4"])

    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().err.lower()


def test_no_subcommand_exits_with_usage(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main([])

    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().err.lower()


def test_version_command_happy_path(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("preloot.cli.bundled_version", lambda: WOWSIMS_VERSION)

    code = main(["version"])

    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "preloot 0.1.0"
    assert out[1] == f"wowsimcli {WOWSIMS_VERSION}"


def test_version_command_from_source_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exe_path = tmp_path / "vendor" / "wowsims" / "wowsimcli.exe"
    exe_path.parent.mkdir(parents=True)
    exe_path.write_bytes(b"binary")
    monkeypatch.setattr("preloot.wowsimcli._repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        "preloot.wowsimcli.subprocess.run",
        lambda args, **kwargs: CompletedProcess(args, 0, stdout=f"{WOWSIMS_VERSION}\n", stderr=""),
    )

    code = main(["version"])

    assert code == 0
    assert capsys.readouterr().out.splitlines() == ["preloot 0.1.0", f"wowsimcli {WOWSIMS_VERSION}"]


def test_version_command_mismatch_returns_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("preloot.cli.bundled_version", lambda: "v0.0.999")

    code = main(["version"])

    assert code == 1
    assert "version mismatch" in capsys.readouterr().err


def test_version_command_wowsimcli_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def _raise() -> str:
        raise WowsimcliError("binary missing")

    monkeypatch.setattr("preloot.cli.bundled_version", _raise)

    code = main(["version"])

    assert code == 1
    assert "binary missing" in capsys.readouterr().err
