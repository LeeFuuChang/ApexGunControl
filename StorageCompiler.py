import xml.etree.ElementTree as ET
import xml.dom.minidom
import requests as rq
import compileall
import shutil
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
        "__pycache__", ".py", ".DS_Store", ".version"
    }

    def walk(root, node, path):
        for child in sorted(os.listdir(path), key=lambda c : os.path.isdir(os.path.join(path, c))):
            if(child in excluding or os.path.splitext(child)[1] in excluding): continue
            childPath = os.path.join(path, child)
            if(os.path.isdir(childPath)):
                childNode = ET.SubElement(node, "folder")
                childNode.attrib["name"] = child
                walk(root, childNode, childPath)
            else:
                fileName, fileType = os.path.splitext(child)
                childNode = ET.SubElement(node, "file")
                childNode.attrib["updated"] = root.attrib["version"]
                childNode.attrib["name"] = fileName
                childNode.attrib["type"] = fileType[1:]
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
        with open(src, "r") as fsrc, open(dst, "w") as fdst:
            fdst.write(rq.post(
                "https://www.toptal.com/developers/html-minifier/api/raw",
                data={"input": re.sub(r"[\n\t\r]", "", fsrc.read())}
            ).text.strip())
    elif(os.path.splitext(src)[1] in {".css", }):
        with open(src, "r") as fsrc, open(dst, "w") as fdst:
            fdst.write(rq.post(
                "https://www.toptal.com/developers/cssminifier/api/raw",
                data={"input": fsrc.read()}
            ).text.strip())
    elif(os.path.splitext(src)[1] in {".js", }):
        with open(src, "r") as fsrc, open(dst, "w") as fdst:
            fdst.write(rq.post(
                "https://www.toptal.com/developers/javascript-minifier/api/raw",
                data={"input": fsrc.read()}
            ).text.strip())
    else:
        shutil.copyfile(src, dst)



if __name__ == "__main__" and len(sys.argv) > 1:
    os.makedirs("compiled_storage", exist_ok=True)
    extractStruct(sys.argv[1], "compiled_storage")
    compileBE(os.path.join(sys.argv[1], "be"), os.path.join("compiled_storage", "be"))
    compileFE(os.path.join(sys.argv[1], "fe"), os.path.join("compiled_storage", "fe"))
    for child in os.listdir(sys.argv[1]):
        if(child in {"be", "fe", "storage.version"}): continue
        shutil.copy(os.path.join(sys.argv[1], child), os.path.join("compiled_storage", child))