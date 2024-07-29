# -*- mode: python ; coding: utf-8 -*-

import json
import sys
import os

name = "ApexGunControl"

working = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))

with open("packages.json", "r") as f:
    imports = json.load(f)

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[p for p in sys.path if working in p and p.endswith("site-packages")],
    binaries=[],
    datas=[(".\\extensions\\*.*", "."), (".\\filled.ico", ".")],
    hiddenimports=[*imports["builtin"], *imports["external"], ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["StorageManager.py", "CLI", f"{name}-LS"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

for d in list(a.datas):
    if "pyconfig" in d[0]:
        a.datas.remove(d)
    if "_C.cp38-win_amd64.pyd" in d[0]:
        a.datas.remove(d)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    uac_admin=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["filled.ico"],
)