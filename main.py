import environment

from LoadingWindow import AbstractLoadingWindow

import importlib, sys, os

import urllib3
urllib3.disable_warnings()

from PackageManager import getPackage
LocalStorage = getattr(getPackage("StorageManager", os.environ["STORAGE_URL"]), "LocalStorage")(os.environ["STORAGE_URL"])

def init():
    loader = AbstractLoadingWindow()
    loader.setIconPath("./default-loading-icon.png")
    loader.setSplashArtPath("./default-loading-splash.png")
    def statusCallback(text, progress):
        nonlocal loader
        loader.text = text
        loader.progress = progress
    loader.setTasks([ lambda : LocalStorage.setup(statusCallback) ])
    loader.exec_()

def main():
    sys.path.append(LocalStorage.path("be"))
    sys.modules["app"] = importlib.import_module("app")
    sys.exit(sys.modules["app"].run())

if __name__ == "__main__": 
    init()
    main()

