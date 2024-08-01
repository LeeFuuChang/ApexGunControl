import xml.etree.ElementTree as ET
import requests as rq
import logging
import shutil
import sys
import os

class LocalStorage:
    latest: int = 0
    version: int = 0

    directory: str = ""
    remoteURL: str = ""
    structure: ET.Element = None

    walkCount: int = 0
    walkTotal: int = 0

    def __new__(cls):
        return cls._instance

    def singletonmethod(func):
        @classmethod
        def ensureInstance(cls, *args, **kwargs):
            if hasattr(cls, "_instance"): return func(cls, *args, **kwargs)
            raise NotImplementedError(
                f"{cls.__name__} has not been setup, no available instance"
            )
        return ensureInstance

    @singletonmethod
    def path(cls, path:str) -> str:
        filepath = os.path.join(cls.directory, path)
        if(not os.path.exists(filepath)):
            _path, _file = os.path.split(path)
            _name, _type = os.path.splitext(_file)
            cls.updateFile(_path=_path,
                           _name=_name,
                           _type=_type[1:])
        return (filepath if(os.path.exists(filepath))else "")

    @singletonmethod
    def updateFile(cls, _path, _name, _type):
        relpath = os.path.join(_path, f"{_name}.{_type}")
        fulpath = os.path.join(cls.directory, relpath)
        urlpath = "/".join([cls.remoteURL, relpath.replace("\\", "/")])
        logging.info(f"[{cls.__name__}] updating: {relpath}")
        try:
            response = rq.get(urlpath, verify=False)
            if(response.status_code//100 == 2):
                os.makedirs(os.path.split(fulpath)[0], exist_ok=True)
                with open(fulpath, "wb") as f: f.write(response.content)
            else:
                raise rq.RequestException(f"Failed {response.status_code}")
        except Exception as e:
            logging.error(f"[{cls.__name__}] update failed: {relpath} {e}")
            if(os.path.exists(os.path.join(cls.directory, relpath))):
                os.remove(os.path.join(cls.directory, relpath))

    @singletonmethod
    def walkUpdate(cls, root, node, dirpath, *, progressCallback=lambda text="",progress=0:0):
        if("--debug" in sys.argv): return node.attrib["name"]

        cls.walkCount += 1

        if(node.tag == "folder"):
            dirpath = os.path.join(dirpath, node.attrib["name"])

            if(not os.path.exists(dirpath)): os.mkdir(dirpath)

            children = {"folder":set(), "file":set(["storage"])}
            for child in node: children[child.tag].add(cls.walkUpdate(root, child, dirpath, progressCallback=progressCallback))

            for child in os.listdir(dirpath):
                childPath = os.path.join(dirpath, child)
                childName = os.path.splitext(child)[0]
                if(childName in children["file"] or childName in children["folder"]): continue
                if(os.path.isfile(childPath)): os.remove(childPath)
                if(os.path.isdir(childPath)): shutil.rmtree(childPath, ignore_errors=True)

        if(node.tag == "file"):
            filepath = os.path.join(dirpath, f"{node.attrib['name']}.{node.attrib['type']}")

            alreadyExist = os.path.exists(filepath)

            if(alreadyExist):
                with open(filepath, "rb") as f:
                    fileContent = f.read()
            else: fileContent = b""

            lastUpdated = int(f"0{node.attrib['updated']}", 16)

            updateCuzStorage = (cls.version < lastUpdated and lastUpdated <= int(f"0{root.attrib['version']}", 16))
            updateCuzMissing = (not alreadyExist)
            updateCuzContent = (not fileContent)

            if(not (updateCuzStorage or updateCuzMissing or updateCuzContent)): return node.attrib["name"]

            reason = f"[CuzStorage({updateCuzStorage}) | CuzMissing({updateCuzMissing}) | CuzContent({updateCuzContent})]"
            logging.info(f"[{cls.__name__}] Updating: {reason} {filepath}")

            cls.updateFile(_path=node.attrib["path"],
                           _name=node.attrib["name"],
                           _type=node.attrib["type"])

            relpath = os.path.join(node.attrib["path"], f"{node.attrib['name']}.{node.attrib['type']}")
            progressCallback(relpath, round(100*cls.walkCount/cls.walkTotal))

        return node.attrib["name"]

    @classmethod
    def setup(cls, remoteURL, executableLOC, *, progressCallback=lambda text="",progress=0:0):
        structure = ET.fromstring(rq.get("/".join([remoteURL, "struct.xml"]), verify=False).text)

        cls.directory = os.path.join(executableLOC, structure.attrib["name"])
        cls.remoteURL = remoteURL
        cls.structure = structure

        cls._instance = object.__new__(cls)

        if(not os.path.exists(cls.directory)): os.mkdir(cls.directory)

        versionFile = os.path.join(cls.directory, "storage.version")
        if(not os.path.exists(versionFile)): open(versionFile, "w").close()
        with open(versionFile, "r") as f: cls.version = int(f"0{f.read()}", 16)

        cls.latest = max(int(f"0{cls.structure.attrib['version']}", 16), cls.version)

        cls.walkCount = 0
        cls.walkTotal = len(cls.structure.findall(".//file")) + len(cls.structure.findall(".//folder")) + 1
        cls.walkUpdate(cls.structure, cls.structure, executableLOC, progressCallback=progressCallback)

        with open(versionFile, "w") as f: f.write(cls.structure.attrib["version"])

        if(cls.latest > cls.version): logging.info(f"[{cls.__name__}] Updated: {cls.version} -> {cls.latest}")

        cls.version = cls.latest

        progressCallback(f"[{cls.__name__}] OK", 100)

        return cls.structure.attrib["name"]
