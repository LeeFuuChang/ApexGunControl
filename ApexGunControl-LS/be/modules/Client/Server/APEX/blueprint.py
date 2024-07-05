import sys
import os

from flask import Blueprint, send_from_directory

Apex = Blueprint("Apex", __name__)

@Apex.route("assets/<path:filepath>")
def Apex_Assets(**kwargs):
    filepath = kwargs["filepath"]
    fullpath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("apex", "assets", filepath))
    return send_from_directory(*os.path.split(fullpath))