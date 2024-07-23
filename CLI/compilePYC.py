import compileall
import sys
import os

sys.pycache_prefix = "/"

excludes = {
    "__pycache__",
    "__init__.py",
}

def compile(src):
    if(os.path.isfile(src)):
        return compileall.compile_file(src, force=True)
    for child in os.listdir(src):
        if(child in excludes): continue
        compile(os.path.join(src, child))
    for child in os.listdir(src):
        if("." not in child): continue
        os.rename(
            os.path.join(src, child),
            os.path.join(src, ".".join(child.split(".")[::child.count(".")]))
        )

if __name__ == "__main__" and len(sys.argv) > 1:
    compile(sys.argv[1])
