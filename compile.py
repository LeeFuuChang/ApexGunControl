from setuptools import setup, Extension
from Cython.Build import cythonize
import shutil, time, os

excludes = {
    "__pycache__",
    "env",
    "installer",
    "LeagueAssistant-LS",
    "compiled",
    "screenshots",
    "check.py",
    "__init__.py",
    "manipulate.py",
    "compile.py",
    "server.py",
    "test.py",
    "LeagueAssistant-Discord.py",
}

def compile_folder(src, dst, hst):
    if(not os.path.exists(hst)): os.mkdir(hst)
    if(not os.path.exists(dst)): os.mkdir(dst)
    building = [os.path.join(src, f) for f in os.listdir(src) if(f.endswith(".py") and f not in excludes)]
    extensions = [Extension(os.path.split(file)[1][:-3], [file]) for file in building]
    setup(ext_modules=cythonize(extensions), language_level=3, script_args=["build_ext", "--inplace", "-b", dst, "-t", dst])
    for file in building: shutil.copy(file, os.path.join(hst, os.path.split(file)[1]))
    shutil.rmtree(os.path.join(dst, "Release"), ignore_errors=True)
    for file in os.listdir(dst):
        path = os.path.join(dst, file)
        if(not os.path.isfile(path)): continue
        os.rename(path, os.path.join(dst, f"{file.split('.')[0]}.{file.split('.')[-1]}"))
    for child in os.listdir(src):
        nsrc = os.path.join(src, child)
        ndst = os.path.join(dst, child)
        nhst = os.path.join(hst, child)
        if(child.endswith(".c")): os.remove(nsrc)
        if(os.path.isdir(nsrc) and child not in excludes): compile_folder(nsrc, ndst, nhst)
        elif(child == "__init__.py"): shutil.copy(nsrc, nhst)

src = "./ApexGunControl-LS/be"
dst = f"./{time.strftime('%Y-%m-%dT%H-%M-%S')}"
hst = dst

compile_folder(src, dst, hst)

for file in os.listdir("."): 
    if file.endswith(".pyd"):
        os.remove(file)

for root, dirs, files in os.walk(src, topdown=False):
    for name in files:
        if(not name.endswith("pyd")): continue
        os.unlink(os.path.join(root, name))