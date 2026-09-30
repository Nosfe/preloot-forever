from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from preloot.cli import main
from preloot.io.artifacts import read_artifact
from preloot.models.settings import Settings
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
    assert payload["schema_version"] == 1
    assert payload["run_id"] == settings_path.parent.name
    assert payload["issues"] == []
    assert payload["target_phase"] == "p4"
    assert payload["previous_phase"] == "p3"
    assert payload["encounter"] == {
        "duration_seconds": 180,
        "duration_variation_seconds": 5,
        "targets": 1,
    }
    assert payload["iterations"] == 12500
    assert payload["seed"] == 1
    assert payload["wowsims_version"] == WOWSIMS_VERSION
    assert payload["source_urls"] == {
        "wowtbc_bis_page_data": "https://wowtbc.gg/page-data/bis-list/{slug}/page-data.json",
        "wowsims_db": f"https://raw.githubusercontent.com/wowsims/tbc-new/{WOWSIMS_VERSION}/assets/database/db.json",
    }


def test_happy_path_p1_sets_previous_phase_to_pre(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"

    code = main(["run", "--workspace", str(workspace), "--phase", "p1"])

    assert code == 0
    settings_path = Path(capsys.readouterr().out.strip())
    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    assert payload["target_phase"] == "p1"
    assert payload["previous_phase"] == "pre"


def test_custom_seed_is_written(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"

    code = main(["run", "--workspace", str(workspace), "--phase", "p4", "--seed", "7"])

    assert code == 0
    settings_path = Path(capsys.readouterr().out.strip())
    payload = json.loads(settings_path.read_text(encoding="utf-8"))
    assert payload["seed"] == 7


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


def test_same_second_collision_keeps_existing_settings_and_returns_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = tmp_path / "workspace"
    run_id = "20260930T120000Z"
    run_dir = workspace / "runs" / "p4" / run_id
    run_dir.mkdir(parents=True)
    settings_path = run_dir / "settings.json"
    original = '{"schema_version":1,"run_id":"old","issues":[],"target_phase":"p4"}'
    settings_path.write_text(original, encoding="utf-8")
    monkeypatch.setattr("preloot.cli._utc_run_id", lambda: run_id)

    code = main(["run", "--workspace", str(workspace), "--phase", "p4"])

    assert code == 1
    err = capsys.readouterr().err
    assert str(settings_path) in err
    assert settings_path.read_text(encoding="utf-8") == original


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


def test_invalid_phase_exits_2_and_lists_choices(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["run", "--workspace", "x", "--phase", "p9"])

    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "invalid choice" in err
    assert "p1" in err
    assert "p2" in err
    assert "p3" in err
    assert "p4" in err
    assert "p5" in err
    assert "{p1,p2,p3,p4,p5}" in err


def test_pre_as_target_is_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["run", "--workspace", "x", "--phase", "pre"])

    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "invalid choice" in err


def test_non_integer_seed_is_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["run", "--workspace", "x", "--phase", "p4", "--seed", "abc"])

    assert exc.value.code == 2
    err = capsys.readouterr().err.lower()
    assert "invalid int value" in err


def test_written_settings_validates_as_settings_artifact(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    workspace = tmp_path / "workspace"

    code = main(["run", "--workspace", str(workspace), "--phase", "p4"])

    assert code == 0
    settings_path = Path(capsys.readouterr().out.strip())
    settings = read_artifact(settings_path, Settings)
    assert settings.wowsims_version == WOWSIMS_VERSION


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
