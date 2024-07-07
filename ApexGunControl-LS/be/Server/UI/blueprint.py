import sys
import os

from flask import Blueprint, send_from_directory

Ui = Blueprint("Ui", __name__)

@Ui.route("/")
def Ui_Root():
    fullpath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("fe", "index.html"))
    return send_from_directory(*os.path.split(fullpath))

@Ui.route("assets/<path:filepath>")
def Ui_Assets(**kwargs):
    filepath = kwargs["filepath"]
    fullpath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("fe", "assets", filepath))
    return send_from_directory(*os.path.split(fullpath))