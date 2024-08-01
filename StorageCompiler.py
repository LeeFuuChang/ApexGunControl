import xml.etree.ElementTree as ET
import distutils.file_util
import distutils.dir_util
import xml.dom.minidom
import requests as rq
import compileall
import sys
import re
import os



def extractStruct(src, dst):
    if(not os.path.exists(src)): raise FileNotFoundError()

    root = ET.Element("folder")
    root.attrib["name"] = os.path.split(src)[1]

    with open(os.path.join(src, "storage.version"), "r") as f:
        root.attrib["version"] = f.read()

    excluding = {
        "__pycache__", ".cli", ".DS_Store", ".version"
    }

    def walk(root, node, path):
        for child in sorted(os.listdir(path), key=lambda c : os.path.isdir(os.path.join(path, c))):
            if(any([x in child for x in list(excluding)])): continue
            childPath = os.path.normpath(os.path.join(path, child))
            if(os.path.isdir(childPath)):
                childNode = ET.SubElement(node, "folder")
                childNode.attrib["name"] = child
                walk(root, childNode, childPath)
            elif(os.path.split(os.path.dirname(childPath))[1] != src):
                fileName, fileType = os.path.splitext(child)
                childNode = ET.SubElement(node, "file")
                childNode.attrib["updated"] = root.attrib["version"]
                childNode.attrib["name"] = fileName
                childNode.attrib["type"] = fileType[1:] if(fileType[1:] != "py")else "pyc"
                childNode.attrib["path"] = os.path.split(os.path.relpath(childPath, src))[0]
    walk(root, root, src)

    with open(os.path.join(dst, "struct.xml"), "w") as f:
        f.write(xml.dom.minidom.parseString(ET.tostring(root, xml_declaration=False)).toprettyxml(indent="\t"))



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
        extractStruct(
            os.path.normpath(sys.argv[1]), 
            os.path.normpath(sys.argv[2]),
        )
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