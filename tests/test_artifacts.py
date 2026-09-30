from __future__ import annotations

import json
from pathlib import Path

import pytest

from preloot.io.artifacts import ArtifactError, read_artifact, write_artifact
from preloot.models.artifacts import Artifact


class ExampleArtifact(Artifact):
    schema_version: int = 3
    payload: str


def test_round_trip_writes_and_reads_indented_utf8_json(tmp_path: Path) -> None:
    path = tmp_path / "example.json"
    expected = ExampleArtifact(run_id="run-1", payload="ok")

    write_artifact(path, expected)
    actual = read_artifact(path, ExampleArtifact)

    assert actual == expected
    text = path.read_text(encoding="utf-8")
    assert "\n  \"schema_version\": 3," in text
    data = json.loads(text)
    assert set(data.keys()) == {"schema_version", "run_id", "issues", "payload"}


def test_killed_before_rename_leaves_target_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "example.json"
    artifact = ExampleArtifact(run_id="run-1", payload="x")

    def _boom(_src: Path, _dst: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr("preloot.io.artifacts.os.replace", _boom)

    with pytest.raises(ArtifactError, match="simulated replace failure"):
        write_artifact(path, artifact)

    assert not path.exists()


def test_target_exists_refuses_overwrite_and_keeps_existing_bytes(tmp_path: Path) -> None:
    path = tmp_path / "example.json"
    original = b"already-there"
    path.write_bytes(original)

    with pytest.raises(ArtifactError, match="target already exists") as exc_info:
        write_artifact(path, ExampleArtifact(run_id="run-1", payload="x"))

    assert exc_info.value.path == path
    assert path.read_bytes() == original


def test_read_invalid_json_raises_artifact_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version": 3, "run_id"', encoding="utf-8")

    with pytest.raises(ArtifactError):
        read_artifact(path, ExampleArtifact)


def test_read_non_utf8_raises_artifact_error(tmp_path: Path) -> None:
    path = tmp_path / "binary.json"
    path.write_bytes(b"\xff\xfe\x00garbage")

    with pytest.raises(ArtifactError):
        read_artifact(path, ExampleArtifact)


def test_read_model_mismatch_raises_artifact_error(tmp_path: Path) -> None:
    path = tmp_path / "missing-field.json"
    path.write_text('{"schema_version": 3, "run_id": "run-1", "issues": []}', encoding="utf-8")

    with pytest.raises(ArtifactError):
        read_artifact(path, ExampleArtifact)


def test_read_old_schema_raises_artifact_error(tmp_path: Path) -> None:
    path = tmp_path / "old-schema.json"
    path.write_text(
        '{"schema_version": 2, "run_id": "run-1", "issues": [], "payload": "x"}',
        encoding="utf-8",
    )

    with pytest.raises(ArtifactError, match="expected 3, found 2"):
        read_artifact(path, ExampleArtifact)


def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        read_artifact(path, ExampleArtifact)


def test_issues_default_is_empty_and_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "issues-default.json"
    artifact = ExampleArtifact(run_id="run-1", payload="x")

    assert artifact.issues == []

    write_artifact(path, artifact)
    loaded = read_artifact(path, ExampleArtifact)
    assert loaded.issues == []
