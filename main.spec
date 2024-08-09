# -*- mode: python ; coding: utf-8 -*-

# pyinstaller main.spec

import sys
import os


PROJECT_NAME = os.path.split(os.getcwd())[1]


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
    checking = [".", os.path.join("locales", "be")]
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

a = Analysis(
    ["main.py"],
    pathex=[os.path.join(r, d) for r, ds, fs in os.walk(os.getcwd()) for d in ds if(d == "site-packages")],
    binaries=[],
    datas=[(".\\filled.ico", "."), ],
    hiddenimports=getPackages(os.path.join("locales", "be")),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["StorageManager.py", "StorageCompiler.py", "locales"],
    noarchive=False,
    optimize=0,
)

for d in list(a.datas):
    if "pyconfig" in d[0]:
        a.datas.remove(d)
    if "_C.cp38-win_amd64.pyd" in d[0]:
        a.datas.remove(d)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=PROJECT_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    uac_admin=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory="plugins",
    icon="filled.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=PROJECT_NAME,
)
