from __future__ import annotations

import hashlib
import importlib.util
import io
import zipfile
from pathlib import Path

import pytest


def _load_fetch_module():
    script_path = Path(__file__).resolve().parents[1] / "tools" / "fetch_wowsimcli.py"
    spec = importlib.util.spec_from_file_location("fetch_wowsimcli", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _zip_payload(binary_content: bytes = b"exe-bytes") -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("wowsimcli-windows.exe", binary_content)
    return out.getvalue()


def _configure_paths(module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vendor_dir = tmp_path / "vendor" / "wowsims"
    monkeypatch.setattr(module, "VENDOR_DIR", vendor_dir)
    monkeypatch.setattr(module, "ZIP_PATH", vendor_dir / module.ZIP_ASSET_NAME)
    monkeypatch.setattr(module, "EXE_PATH", vendor_dir / "wowsimcli.exe")


def test_build_url_uses_pinned_version() -> None:
    module = _load_fetch_module()

    url = module.build_url()

    assert "/v0.0.145/" in url
    assert url.endswith("/wowsimcli-windows.exe.zip")


def test_fetch_clean_downloads_and_extracts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_fetch_module()
    _configure_paths(module, tmp_path, monkeypatch)

    payload = _zip_payload()
    monkeypatch.setattr(module, "ZIP_SHA256", hashlib.sha256(payload).hexdigest())
    monkeypatch.setattr(module.truststore, "inject_into_ssl", lambda: None)
    monkeypatch.setattr(module, "download_zip", lambda url: payload)

    code = module.main()

    assert code == 0
    assert module.ZIP_PATH.exists()
    assert module.EXE_PATH.exists()


def test_fetch_existing_zip_skips_download_and_reextracts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_fetch_module()
    _configure_paths(module, tmp_path, monkeypatch)

    payload = _zip_payload(binary_content=b"expected")
    expected_hash = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(module, "ZIP_SHA256", expected_hash)
    monkeypatch.setattr(module.truststore, "inject_into_ssl", lambda: None)

    module.VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    module.ZIP_PATH.write_bytes(payload)

    def _no_download(url: str) -> bytes:
        raise AssertionError("download should not run when cached zip hash is valid")

    monkeypatch.setattr(module, "download_zip", _no_download)

    code = module.main()

    assert code == 0
    assert module.EXE_PATH.read_bytes() == b"expected"


def test_fetch_bad_hash_cleans_and_exits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _load_fetch_module()
    _configure_paths(module, tmp_path, monkeypatch)

    payload = _zip_payload()
    monkeypatch.setattr(module, "ZIP_SHA256", "0" * 64)
    monkeypatch.setattr(module.truststore, "inject_into_ssl", lambda: None)
    monkeypatch.setattr(module, "download_zip", lambda url: payload)

    code = module.main()

    assert code == 1
    err = capsys.readouterr().err
    assert "sha256 mismatch" in err
    assert "0" * 64 in err
    assert hashlib.sha256(payload).hexdigest() in err
    assert not module.ZIP_PATH.exists()
    assert not module.EXE_PATH.exists()
