from flask import Blueprint, send_from_directory
from PackageManager import getPackage
import os

Ui = Blueprint("Ui", __name__)

@Ui.route("/")
def Ui_Root():
    StorageManager = getPackage("StorageManager", os.environ["STORAGE_URL"])
    LocalStorage = getattr(StorageManager, "LocalStorage").getInstance()
    fullpath = LocalStorage.path(os.path.join("fe", "index.html"))
    return send_from_directory(*os.path.split(fullpath))

@Ui.route("assets/<path:filepath>")
def Ui_Assets(**kwargs):
    filepath = kwargs["filepath"]
    StorageManager = getPackage("StorageManager", os.environ["STORAGE_URL"])
    LocalStorage = getattr(StorageManager, "LocalStorage").getInstance()
    fullpath = LocalStorage.path(os.path.join("fe", "assets", filepath))
    return send_from_directory(*os.path.split(fullpath))