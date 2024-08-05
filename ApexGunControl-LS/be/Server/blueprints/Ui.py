from flask import Blueprint, send_file
import sys


Ui = Blueprint("Ui", __name__)


@Ui.route("/")
def Ui_Root():
    return send_file(sys.modules["StorageManager"].LocalStorage.path("fe", "index.html"))


@Ui.route("assets/<path:filepath>")
def Ui_Assets(**kwargs):
    return send_file(sys.modules["StorageManager"].LocalStorage.path("fe", "assets", kwargs["filepath"]))
