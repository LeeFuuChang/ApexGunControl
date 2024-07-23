# -*- mode: python ; coding: utf-8 -*-

block_cipher = pyi_crypto.PyiBlockCipher(key='helloworldishard')

a = Analysis(
    ["main.py"],
    pathex=['.\\env\\Lib\\site-packages'],
    binaries=[],
    datas=[],
    hiddenimports=["environment.py"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

for d in list(a.datas):
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
    if '_C.cp38-win_amd64.pyd' in d[0]:
        a.datas.remove(d)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LeagueAssistant-4.3.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    uac_admin=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['.\\LeagueAssistant-LS\\logo\\Filled.ico'],
)