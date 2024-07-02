import shutil
import sys
import os

import urllib3
urllib3.disable_warnings()

import logging
logger = logging.getLogger()

import xml.etree.ElementTree as ET
import requests as rq



class LocalStorage:
    remoteURL: str = ""
    directory: str = ""
    structure: ET.Element = None


    def __new__(cls):
        if hasattr(cls, "_instance"): return cls._instance
        raise NotImplementedError(f"{cls.__name__} has not been setup, no instance can be returned")


    @staticmethod
    def updateFile(remoteURL, directory, _root, _path, _name, _type):
        fileName = f"{_name}.{_type}"
        targetPath = os.path.join(directory, _root.attrib["name"], _path, fileName)
        sourcePath = os.path.join(remoteURL, _path, f"{_name}.{_type}")
        fileFailed = True
        try:
            response = rq.get(sourcePath.replace("\\", "/"), verify=False)
            if(response.status_code//100 == 2):
                fileFailed = False
                os.makedirs(os.path.dirname(targetPath), exist_ok=True)
                with open(targetPath, "wb") as f: f.write(response.content)
            else: logger.info(f"LS-Update failed on {(_path, _name, _type)} {response}")
        except Exception as e: logger.error(f"LS-Update error on {(_path, _name, _type)} {e}")
        if(fileFailed and os.path.exists(targetPath)): os.remove(targetPath)


    @classmethod
    def setup(cls, remoteURL, directory, progressCallback=lambda current=0,total=0:0) -> str:
        structure = ET.fromstring(rq.get(os.path.join(remoteURL, "struct.xml").replace("\\", "/"), verify=False).text)

        cls._instance = object.__new__(cls)
        cls._instance.remoteURL = remoteURL
        cls._instance.directory = directory
        cls._instance.structure = structure

        if(not os.path.exists(os.path.join(directory, structure.attrib["name"]))):
            os.mkdir(os.path.join(directory, structure.attrib["name"]))

        versionFile = os.path.join(directory, structure.attrib["name"], "storage.version")
        if(not os.path.exists(versionFile)): open(versionFile, "w").close()
        with open(versionFile, "r") as f: currentHexVersion = f.read()

        CHVN = int(f"0{currentHexVersion}", 16)
        LHVN = int(f"0{structure.attrib['version']}", 16)
        if(LHVN > CHVN): logger.info(f"Updating storage from {CHVN} to {LHVN}")

        totalCount = len(structure.findall(".//file")) + len(structure.findall(".//folder")) + 1
        checkCount = 0

        def walk(root, parent, path):
            nonlocal progressCallback, totalCount, checkCount
            path = os.path.join(path, parent.attrib["name"])
            if(parent.tag == "folder"):
                checkCount += 1
                if(not os.path.exists(path)): os.mkdir(path)
                children = {"folder":set(), "file":set(), "type":set(["version"])}
                for child in parent: children[child.tag].add(walk(root, child, path))
                if(getattr(sys, "frozen", False)):
                    for child in os.listdir(path):
                        childPath = os.path.join(path, child)
                        childName, childType = os.path.splitext(child)
                        if(childType[1:] in children["type"]): continue
                        needed_file = (os.path.isfile(childPath) and childName in children["file"]) 
                        needed_dir = (os.path.isdir(childPath) and childName in children["folder"]) 
                        if(needed_file or needed_dir): continue
                        if(os.path.isfile(childPath)): os.remove(childPath)
                        else: shutil.rmtree(childPath, ignore_errors=True)
            elif(parent.tag == "file"):
                checkCount += 1
                filePath = f"{path}.{parent.attrib['type']}"
                lastUpdatedOnVersion = int(f"0{parent.attrib['updated']}", 16)
                alreadyExist = os.path.exists(filePath)
                if(alreadyExist):
                    with open(filePath, "rb") as f: fileContent = f.read()
                else: fileContent = b""
                updateCuzStorage = (CHVN<lastUpdatedOnVersion and lastUpdatedOnVersion<=LHVN)
                updateCuzMissing = (not alreadyExist)
                updateCuzContent = (not fileContent)
                needUpdateFile = (updateCuzStorage or updateCuzMissing or updateCuzContent)
                fileInfoString = f"{parent.attrib['name']:>15} {parent.attrib['type']:>5} {parent.attrib['path']}"
                if(not needUpdateFile): return parent.attrib["name"]
                elif(updateCuzStorage): logger.info(f"{root.attrib['name']}-Update: [Cuz: Storage] {fileInfoString}")
                elif(updateCuzMissing): logger.info(f"{root.attrib['name']}-Update: [Cuz: Missing] {fileInfoString}")
                elif(updateCuzContent): logger.info(f"{root.attrib['name']}-Update: [Cuz: Content] {fileInfoString}")
                cls.updateFile( remoteURL=remoteURL,
                                directory=directory,
                                _root=root,
                                _path=parent.attrib["path"],
                                _name=parent.attrib["name"],
                                _type=parent.attrib["type"])
                progressCallback("Updating . . .", round(checkCount/totalCount*100))
            return parent.attrib["name"]

        rootName = walk(structure, structure, directory)

        with open(os.path.join(directory, structure.attrib["name"], "storage.version"), "w") as f: f.write(structure.attrib["version"])

        progressCallback("Storage OK . . .", round(checkCount/totalCount*100))

        return rootName


    def path(self, path:str) -> str:
        filePath = os.path.normpath(os.path.join(self.directory, self.structure.attrib["name"], path))
        if(not os.path.exists(filePath)): 
            _path, _file = os.path.split(path)
            _name, _type = os.path.splitext(_file)
            self.updateFile(remoteURL=self.remoteURL,
                            directory=self.directory,
                            _root=self.structure,
                            _path=_path,
                            _name=_name,
                            _type=_type[1:])
        return (filePath if(os.path.exists(filePath))else "")




