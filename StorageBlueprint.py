from flask import Blueprint, send_file, redirect, Response
import xml.etree.ElementTree as ET
from datetime import datetime
from . import _Constants
import json
import os

PROJECT_NAME = "ApexGunControl"
PROJECT_PATH = os.path.join(os.path.dirname(__file__), "ProjectFiles", PROJECT_NAME)

project = Blueprint(PROJECT_NAME, __name__)





@project.route("", methods=["GET"])
def ApexGunControl():
    _Constants.PROJECT_LOGGER.info(f"[{PROJECT_NAME}-Main] OK")
    return redirect("https://leefuuchang.github.io/ApexGunControl/")





#normal endpoints
@project.route("Version", methods=["GET"])
def ApexGunControl_Version():
    structPath = os.path.join(PROJECT_PATH, "Storage", "struct.xml")
    if(not os.path.exists(structPath)): return Response(status=404)

    lastEditTime = os.path.getmtime(structPath)

    with open(structPath, "r") as f: structure = ET.fromstring(f.read())

    _Constants.PROJECT_LOGGER.info(f"[{PROJECT_NAME}-Version] OK")
    return {
        "version": structure.attrib["version"],
        "last-edit": datetime.fromtimestamp(lastEditTime).strftime(r"%Y-%m-%d %H:%M:%S"),
    }

@project.route("Download", methods=["GET"])
def ApexGunControl_Download():
    ApexGunControl_Log_file = os.path.join(PROJECT_PATH, "Data", f"{PROJECT_NAME}_Log.json")
    with open(ApexGunControl_Log_file, "r") as Log_File:
        Current_Log = json.load(Log_File)
    Latest_Patch = Current_Log["Patch"]

    _Constants.PROJECT_LOGGER.info(f"[{PROJECT_NAME}-Download] OK")
    return send_file(
        os.path.join(PROJECT_PATH, "Releases", f"{PROJECT_NAME}-{Latest_Patch}.exe"),
        as_attachment=True
    )

