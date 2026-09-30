a = Analysis(
    ["src/preloot/__main__.py"],
    pathex=["src"],
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
