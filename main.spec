# -*- mode: python ; coding: utf-8 -*-

# pyinstaller --distpath . --upx-dir ./upx main.spec

import environment
import json
import sys
import os


def extractImports(path):
    with open(path) as f:
        statements = [f"{line} as _" for line in f.readlines() if "import " in line]
        imported = [
            *[sm[sm.index("from"):sm.index("import")][4:].strip() for sm in statements if "from" in sm],
            *[sm[sm.index("import"):sm.index(" as ")][6:].strip() for sm in statements if "from" not in sm],
        ]
    return [pack for pack in imported if not pack.startswith(".")]

def filterLocal(name):
    root = name.split(".")[0]
    checking = [".", os.path.join(f"{os.environ['PROJECT_NAME']}-LS", "be")]
    return not any([os.path.exists(p) for p in [
        *[os.path.join(r, root) for r in checking],
        *[os.path.join(r, f"{root}.py") for r in checking],
    ]])

def getPackages(bepath):
    packages = set()
    for root, dirs, files in os.walk(bepath):
        for file in files:
            if(os.path.splitext(file)[1] != ".py"): continue
            packages = packages.union(extractImports(os.path.join(root, file)))
    packages = packages.union(extractImports("StorageManager.py"))
    packages = packages.union(extractImports("environment.py"))
    packages = packages.union(extractImports("main.py"))
    return list(filter(filterLocal, list(packages)))


working = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[p for p in sys.path if working in p and p.endswith("site-packages")],
    binaries=[],
    datas=[(".\\filled.ico", "."), ],
    hiddenimports=getPackages(os.path.join(f"{os.environ['PROJECT_NAME']}-LS", "be")),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["StorageManager.py", "StorageCompiler.py", f"{os.environ['PROJECT_NAME']}-LS"],
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
    name=os.environ["PROJECT_NAME"],
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