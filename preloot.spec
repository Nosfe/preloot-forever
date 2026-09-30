from pathlib import Path


WOWSIMCLI_PATH = Path("vendor/wowsims/wowsimcli.exe")
if not WOWSIMCLI_PATH.exists():
    raise SystemExit(
        "Missing bundled binary: vendor/wowsims/wowsimcli.exe. "
        "Run 'uv run python tools/fetch_wowsimcli.py' before building."
    )


a = Analysis(
    ["src/preloot/__main__.py"],
    pathex=["src"],
    binaries=[(str(WOWSIMCLI_PATH), "wowsims")],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="preloot",
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="preloot",
)
