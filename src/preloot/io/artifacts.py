from __future__ import annotations

import os
from pathlib import Path
from typing import TypeVar

from pydantic import ValidationError

from preloot.models.artifacts import Artifact

A = TypeVar("A", bound=Artifact)


class ArtifactError(RuntimeError):
    def __init__(self, path: Path, cause: BaseException) -> None:
        self.path = path
        self.cause = cause
        super().__init__(f"artifact error at {path}: {cause}")


def write_artifact(path: Path, artifact: Artifact) -> None:
    if path.exists():
        raise ArtifactError(path, FileExistsError("target already exists"))

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp")

    try:
        payload = artifact.model_dump_json(indent=2)
        with tmp_path.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())

        type(artifact).model_validate_json(tmp_path.read_text(encoding="utf-8"))
        os.replace(tmp_path, path)
    except Exception as exc:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise ArtifactError(path, exc) from exc


def read_artifact(path: Path, model: type[A]) -> A:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ArtifactError(path, exc) from exc

    try:
        artifact = model.model_validate_json(raw)
    except ValidationError as exc:
        raise ArtifactError(path, exc) from exc

    expected = model.model_fields["schema_version"].default
    found = artifact.schema_version
    if expected is None:
        raise ArtifactError(path, ValueError("model schema_version must define a default"))
    if found != expected:
        raise ArtifactError(path, ValueError(f"schema_version mismatch: expected {expected}, found {found}"))

    return artifact
