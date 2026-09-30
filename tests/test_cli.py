from __future__ import annotations

import json
from pathlib import Path

import pytest

from preloot.cli import main


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
