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

    @staticmethod
    def join(*paths:str) -> str:
        return os.path.normpath(os.path.join(*paths)).replace("\/", os.sep).replace("\\", os.sep)

    @singletonmethod
    def path(cls, *paths:str) -> str:
        filepath = cls.join(cls.directory, *paths)
        if(not os.path.exists(filepath)):
            _path, _file = os.path.split(filepath)
            _name, _type = os.path.splitext(_file)
            cls.updateFile(_path=_path,
                           _name=_name,
                           _type=_type[1:])
        return (filepath if(os.path.exists(filepath))else "")

    @singletonmethod
    def updateRel(cls, relpath:str) -> None:
        subpath = os.path.relpath(relpath, os.path.split(cls.directory)[1])
        fulpath = cls.join(cls.directory, subpath)
        urlpath = "/".join([cls.remoteURL, subpath.replace("\\", "/")])
        logging.info(f"[{cls.__name__}] updateFile: '{urlpath}' -> '{fulpath}'")
        if("--debug" in sys.argv):
            logging.info(f"[{cls.__name__}] updateFile canceled duo to debug mode")
            return
        try:
            response = rq.get(urlpath, verify=False)
            if(response.status_code//100 == 2):
                os.makedirs(os.path.split(fulpath)[0], exist_ok=True)
                with open(fulpath, "wb") as f: f.write(response.content)
            else:
                raise rq.RequestException(f"{response.status_code}")
        except Exception as e:
            logging.error(f"[{cls.__name__}] updateFile failed: {fulpath} {e}")
            if(os.path.exists(fulpath)): os.remove(fulpath)

    @singletonmethod
    def removeRel(cls, relpath:str) -> None:
        subpath = os.path.relpath(relpath, os.path.split(cls.directory)[1])
        fulpath = cls.join(cls.directory, subpath)
        logging.info(f"[{cls.__name__}] removeRel: '{fulpath}'")
        if("--debug" in sys.argv):
            logging.info(f"[{cls.__name__}] removeRel canceled duo to debug mode")
            return
        if(os.path.isfile(fulpath)): os.remove(fulpath)
        if(os.path.isdir(fulpath)): shutil.rmtree(fulpath, ignore_errors=True)

    @singletonmethod
    def walkUpdate(cls, root:ET.Element, node:ET.Element, exepath:str, relpath:str, *, progressCallback=lambda text="",progress=0:0) -> str:

        cls.walkCount += 1

        if(node.tag == "folder"):
            relpath = cls.join(relpath, node.attrib["name"])
            fulpath = cls.join(exepath, relpath)

            if(not os.path.exists(fulpath)): os.mkdir(fulpath)

            children = {"folder":set(), "file":set(["storage"])}
            for child in node: children[child.tag].add(cls.walkUpdate(root, child, exepath, relpath, progressCallback=progressCallback))

            for child in os.listdir(fulpath):
                childName = os.path.splitext(child)[0]
                if(childName in children["file"] or childName in children["folder"]): continue
                cls.removeRel(relpath=cls.join(relpath, child))

        if(node.tag == "file"):
            relpath = cls.join(relpath, f"{node.attrib['name']}.{node.attrib['type']}")
            fulpath = cls.join(exepath, relpath)

            alreadyExist = os.path.exists(fulpath)

            if(alreadyExist):
                with open(fulpath, "rb") as f:
                    fileContent = f.read()
            else: fileContent = b""

            lastUpdated = int(f"0{node.attrib['updated']}", 16)

            updateCuzStorage = (cls.version < lastUpdated and lastUpdated <= int(f"0{root.attrib['version']}", 16))
            updateCuzMissing = (not alreadyExist)
            updateCuzContent = (not fileContent)

            if(not (updateCuzStorage or updateCuzMissing or updateCuzContent)): return node.attrib["name"]

            reason = f"[CuzStorage({updateCuzStorage}) | CuzMissing({updateCuzMissing}) | CuzContent({updateCuzContent})]"
            logging.info(f"[{cls.__name__}] Updating: {reason} '{fulpath}'")

            cls.updateRel(relpath=relpath)

            progressCallback(relpath, round(100*cls.walkCount/cls.walkTotal))

        return node.attrib["name"]

    @classmethod
    def setup(cls, remoteURL:str, executableLOC:str, *, progressCallback=lambda text="",progress=0:0) -> str:
        structure = ET.fromstring(rq.get("/".join([remoteURL, "struct.xml"]), verify=False).text)

        try:
            if(os.path.exists(cls.join(executableLOC, structure.attrib["name"]))):
                shutil.rmtree(cls.join(executableLOC, "locales"), ignore_errors=True)
                os.rename(cls.join(executableLOC, structure.attrib["name"]), cls.join(executableLOC, "locales"))
        except:
            shutil.rmtree(cls.join(executableLOC, structure.attrib["name"]), ignore_errors=True)
        finally:
            structure.attrib["name"] = "locales"

        cls.directory = cls.join(executableLOC, structure.attrib["name"])
        cls.remoteURL = remoteURL
        cls.structure = structure

        cls._instance = object.__new__(cls)

        if(not os.path.exists(cls.directory)): os.mkdir(cls.directory)

        versionFile = cls.join(cls.directory, "storage.version")
        if(not os.path.exists(versionFile)): open(versionFile, "w", encoding="UTF-8").close()
        with open(versionFile, "r", encoding="UTF-8") as f: cls.version = int(f"0{f.read()}", 16)

        cls.latest = max(int(f"0{cls.structure.attrib['version']}", 16), cls.version)

        cls.walkCount = 0
        cls.walkTotal = len(cls.structure.findall(".//file")) + len(cls.structure.findall(".//folder")) + 1
        cls.walkUpdate(cls.structure, cls.structure, executableLOC, "", progressCallback=progressCallback)

        with open(versionFile, "w", encoding="UTF-8") as f: f.write(hex(cls.latest)[2:].upper())

        if(cls.latest > cls.version): logging.info(f"[{cls.__name__}] Updated: {cls.version} -> {cls.latest}")

        cls.version = cls.latest

        progressCallback(f"[{cls.__name__}] OK", 100)

        return cls.structure.attrib["name"]
