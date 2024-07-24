import environment
environment.RemoteImport("StorageManager")

import importlib
import sys
import os

import urllib3
urllib3.disable_warnings()

from LoadingWindow import LoadingWindow

LocalStorage = sys.modules["StorageManager"].LocalStorage

def init():
    loader = LoadingWindow()
    loader.setIconURL(f"{os.environ['STORAGE_URL']}/LoadingIcon.png")
    loader.setSplashArtURL(f"{os.environ['STORAGE_URL']}/LoadingSplash.jpg")
    def statusCallback(text, progress):
        nonlocal loader
        loader.text = text
        loader.progress = progress
    loader.setTasks([ lambda : LocalStorage.setup(
        os.environ["STORAGE_URL"],
        os.environ["EXECUTABLE_ROOT"],
        progressCallback=statusCallback,
    ) ])
    loader.exec_()

def main():
    sys.path.append(LocalStorage.path("be"))
    sys.modules["app"] = importlib.import_module("app")
    sys.exit(sys.modules["app"].run())

if __name__ == "__main__": 
    init()
    main()

