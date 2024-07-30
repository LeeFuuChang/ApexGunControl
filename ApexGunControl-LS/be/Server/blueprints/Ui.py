from flask import Blueprint, send_file
import sys
import os


Ui = Blueprint("Ui", __name__)


@Ui.route("/")
def Ui_Root():
    return send_file(sys.modules["StorageManager"].LocalStorage.path(os.path.join("fe", "index.html")))


@Ui.route("assets/<path:filepath>")
def Ui_Assets(**kwargs):
    return send_file(sys.modules["StorageManager"].LocalStorage.path(os.path.join("fe", "assets", kwargs["filepath"])))
