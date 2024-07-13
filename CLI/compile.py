from setuptools import setup, Extension
from Cython.Build import cythonize
import shutil, sys, os

excludes = {
    "__pycache__",
    "__init__.py",
}

def compile(src):
    building = [os.path.join(src, f) for f in os.listdir(src) if(f.endswith(".py") and f not in excludes)]
    extensions = [Extension(os.path.split(file)[1][:-3], [file]) for file in building]
    setup(ext_modules=cythonize(extensions), language_level=3, script_args=["build_ext", "--inplace", "-b", src])
    for child in os.listdir(src):
        if(child in excludes): continue
        nsrc = os.path.join(src, child)
        if(os.path.isdir(nsrc)): 
            compile(nsrc)
        elif(child.endswith(".c")):
            os.remove(nsrc)
        elif(os.path.exists(child) and not os.path.samefile(child, nsrc)):
            os.remove(child)
        else:
            print("rename", nsrc, os.path.join(src, ".".join(child.split(".")[::child.count(".")])))
            os.rename(nsrc, os.path.join(src, ".".join(child.split(".")[::child.count(".")])))


if __name__ == "__main__" and len(sys.argv) > 1:
    compile(sys.argv[1])

    shutil.rmtree("build", ignore_errors=True)

    for root, dirs, files in os.walk(sys.argv[1], topdown=False):
        for name in files:
            os.rename(
                os.path.join(root, name),
                os.path.join(root, ".".join(name.split(".")[::name.count(".")]))
            )