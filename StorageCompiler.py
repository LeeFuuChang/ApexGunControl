import distutils.file_util
import distutils.dir_util
import requests as rq
import compileall
import sys
import re
import os



def compileBE(src, dst):
    sys.pycache_prefix = "/"

    excludes = {
        "__pycache__",
        "__init__.py",
    }

    if(os.path.isfile(src)):
        return compileall.compile_file(src, force=True)

    for child in os.listdir(src):
        if(child in excludes): continue
        compileBE(os.path.join(src, child), os.path.join(dst, child))

    for child in os.listdir(src):
        if(os.path.splitext(child)[1] != ".pyc"): continue
        if(child in excludes or "." not in child): continue
        os.makedirs(dst, exist_ok=True)
        os.rename(
            os.path.join(src, child),
            os.path.join(dst, ".".join(child.split(".")[::child.count(".")]))
        )



def compileFE(src, dst):
    if(os.path.isdir(src)):
        os.makedirs(dst, exist_ok=True)
        for child in os.listdir(src):
            compileFE(
                os.path.join(src, child),
                os.path.join(dst, child),
            )
    elif(os.path.splitext(src)[1] in {".html", ".svg"}):
        print(f"Compiling '{src}'...")
        with open(src, "r", encoding="utf-8") as fsrc, open(dst, "w", encoding="utf-8") as fdst:
            fdst.write(rq.post(
                "https://www.toptal.com/developers/html-minifier/api/raw",
                data={"input": re.sub(r"[\n\t\r]", "", fsrc.read())}
            ).text.strip())
    elif(os.path.splitext(src)[1] in {".css", }):
        print(f"Compiling '{src}'...")
        with open(src, "r", encoding="utf-8") as fsrc, open(dst, "w", encoding="utf-8") as fdst:
            fdst.write(rq.post(
                "https://www.toptal.com/developers/cssminifier/api/raw",
                data={"input": fsrc.read()}
            ).text.strip())
    elif(os.path.splitext(src)[1] in {".js", }):
        print(f"Compiling '{src}'...")
        with open(src, "r", encoding="utf-8") as fsrc, open(dst, "w", encoding="utf-8") as fdst:
            fdst.write(rq.post(
                "https://www.toptal.com/developers/javascript-minifier/api/raw",
                data={"input": fsrc.read()}
            ).text.strip())
    else:
        print(f"Compiling '{src}'...")
        distutils.file_util.copy_file(src, dst)



if __name__ == "__main__" and len(sys.argv) == 3:
    if(os.path.exists(os.path.dirname(sys.argv[2]))):
        if(os.path.exists(sys.argv[2])):
            distutils.dir_util.remove_tree(sys.argv[2])
        os.mkdir(sys.argv[2])
        compileBE(
            os.path.normpath(os.path.join(sys.argv[1], "be")),
            os.path.normpath(os.path.join(sys.argv[2], "be")),
        )
        # compileFE(
        #     os.path.normpath(os.path.join(sys.argv[1], "fe")),
        #     os.path.normpath(os.path.join(sys.argv[2], "fe")),
        # )
        for child in os.listdir(sys.argv[1]):
            if(child in {
                "be",
                # "fe",
                "storage.version",
            }): continue
            src = os.path.join(sys.argv[1], child)
            dst = os.path.join(sys.argv[2], child)
            if(os.path.isdir(src)):
                distutils.dir_util.copy_tree(src, dst)
            if(os.path.isfile(src)):
                distutils.file_util.copy_file(src, dst)
    else:
        raise FileNotFoundError(sys.argv[2])
else:
    raise ValueError(f"argv length: {len(sys.argv)}")