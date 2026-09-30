from __future__ import annotations

import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import truststore

from preloot.models.wowsims import WOWSIMS_VERSION

ZIP_SHA256 = "0fda61b945e0045c25b69854af8017183576ecf3404f1f0bd4bd74d92bc118a1"
ZIP_ASSET_NAME = "wowsimcli-windows.exe.zip"
ZIP_MEMBER_NAME = "wowsimcli-windows.exe"

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = REPO_ROOT / "vendor" / "wowsims"
ZIP_PATH = VENDOR_DIR / ZIP_ASSET_NAME
EXE_PATH = VENDOR_DIR / "wowsimcli.exe"


def build_url() -> str:
    return (
        "https://github.com/wowsims/tbc-new/releases/download/"
        f"{WOWSIMS_VERSION}/{ZIP_ASSET_NAME}"
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download_zip(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "preloot/0.1.0 wowsimcli-fetch"},
    )
    with urllib.request.urlopen(request) as response:
        return response.read()


def ensure_verified_zip(download_fn=None) -> None:
    if download_fn is None:
        download_fn = download_zip

    if ZIP_PATH.exists():
        existing_hash = _sha256_file(ZIP_PATH)
        if existing_hash == ZIP_SHA256:
            return
        ZIP_PATH.unlink(missing_ok=True)
        EXE_PATH.unlink(missing_ok=True)

    payload = download_fn(build_url())
    actual_hash = _sha256_bytes(payload)
    if actual_hash != ZIP_SHA256:
        ZIP_PATH.unlink(missing_ok=True)
        EXE_PATH.unlink(missing_ok=True)
        raise ValueError(
            "sha256 mismatch for wowsimcli zip: "
            f"expected {ZIP_SHA256}, got {actual_hash}"
        )

    ZIP_PATH.write_bytes(payload)


def extract_exe_if_missing() -> None:
    if EXE_PATH.exists():
        return

    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        try:
            with archive.open(ZIP_MEMBER_NAME, "r") as source:
                EXE_PATH.write_bytes(source.read())
        except KeyError as exc:
            raise RuntimeError(
                f"zip archive is missing expected member: {ZIP_MEMBER_NAME}"
            ) from exc


def main() -> int:
    truststore.inject_into_ssl()
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)

    try:
        ensure_verified_zip()
        extract_exe_if_missing()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Prepared {EXE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
