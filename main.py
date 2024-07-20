import environment
import importlib
import sys
import os

import urllib3
urllib3.disable_warnings()

from LoadingWindow import LoadingWindow

from PackageManager import getPackage
LocalStorage = getattr(getPackage("StorageManager", os.environ["STORAGE_URL"]), "LocalStorage")

def init():
    loader = LoadingWindow()
    loader.setIconPath(f"{os.environ['STORAGE_URL']}/LoadingIcon.png")
    loader.setSplashArtURL(f"{os.environ['STORAGE_URL']}/LoadingSplash.jpg")
    def statusCallback(text, progress):
        nonlocal loader
        loader.text = text
        loader.progress = progress
    loader.setTasks([ lambda : LocalStorage.setup(os.environ["STORAGE_URL"], os.environ["EXECUTABLE_ROOT"], statusCallback) ])
    loader.exec_()

def main():
    sys.path.append(LocalStorage().path("be"))
    sys.modules["app"] = importlib.import_module("app")
    sys.exit(sys.modules["app"].run())

if __name__ == "__main__": 
    init()
    main()

