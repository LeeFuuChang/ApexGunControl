# -*- mode: python ; coding: utf-8 -*-

import sys
import os

working = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))

block_cipher = pyi_crypto.PyiBlockCipher(key="helloworldishard")

a = Analysis(
    ["main.py"],
    pathex=[p for p in sys.path if working in p and p.endswith("site-packages")],
    binaries=[],
    datas=[(".\\extensions\\*.*", "."), ],
    hiddenimports=["environment.py"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["StorageManager.py"],
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
    name="ApexGunControl",
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