from datetime import datetime
from pytz import timezone
import requests as rq
import json
import sys
import os

from flask import Blueprint, send_from_directory, request, Response

App = Blueprint("App", __name__)

@App.route("/login", methods=["POST"])
def App_Login():
    res = rq.post(
        f"{os.environ['SERVER_URL']}/Login",
        data={
            "username": request.form.get("username", ""),
            "password": request.form.get("password", ""),
        })

    try: data = res.json()
    except: data = {}

    os.environ["USERNAME"]  = data.get("username", "")
    os.environ["PASSWORD"]  = data.get("password", "")
    os.environ["EXPIRE_AT"] = data.get("expireAt", "")

    return {
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "expireAt": os.environ["EXPIRE_AT"],
    }, res.status_code



@App.route("/activate", methods=["POST"])
def App_Activate():
    res = rq.post(
        f"{os.environ['SERVER_URL']}/Activate",
        data={
            "username": os.environ["USERNAME"],
            "password": os.environ["PASSWORD"],
            "pin"     : request.form.get("pin", ""),
        })

    try: data = res.json()
    except: data = {}

    os.environ["USERNAME"]  = data.get("username", "")
    os.environ["PASSWORD"]  = data.get("password", "")
    os.environ["EXPIRE_AT"] = data.get("expireAt", "")

    return {
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "expireAt": os.environ["EXPIRE_AT"],
    }, res.status_code



@App.route("/logout", methods=["POST"])
def App_Logout():
    os.environ["USERNAME"] = ""
    os.environ["PASSWORD"] = ""
    os.environ["EXPIRE_AT"] = ""
    return {
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "expireAt": os.environ["EXPIRE_AT"],
    }, 200



@App.route("/auth-state", methods=["POST"])
def App_AuthState():
    now = datetime.now(tz=timezone("Asia/Taipei"))
    authorized = os.environ["EXPIRE_AT"] > now.strftime(r"%Y/%m/%d %H:%M:%S")
    return os.environ["EXPIRE_AT"] if(authorized)else ""



@App.route("/version", methods=["GET"])
def App_Version():
    versionPath = sys.modules["StorageManager"].LocalStorage().path("storage.version")
    if(not versionPath or not os.path.exists(versionPath)): return Response(status=404)

    with open(versionPath, "r") as f: currentVersion = f.read()

    latest = rq.get(f"{os.environ['SERVER_URL']}/Version").json()

    return {
        "current-version": currentVersion,
        "latest-version": latest["version"],
        "release-date": latest["last-edit"],
    }



App.control_functions = {}
@App.route("/controls/<string:name>", methods=["POST"])
def App_Controls(**kwargs):
    name = kwargs["name"]
    if(name not in App.control_functions): return Response(status=404)
    try: data = request.get_json(force=True)
    except: data = []
    App.control_functions[name](*data)
    return Response(status=200)



@App.route("/config/<path:filepath>", methods=["GET", "POST"])
def App_Config(**kwargs):
    kwargs['filepath'] = kwargs['filepath'] or "app.json"

    configPath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("cfg", kwargs["filepath"]))

    if(not configPath): return Response(status=404)

    if(os.path.isdir(configPath)): return os.listdir(configPath)

    if(request.method == "GET"):
        return send_from_directory(*os.path.split(configPath))
    elif(request.method == "POST"):
        try:
            data = request.get_json(force=True)
            with open(configPath, "a+") as f:
                f.seek(0)
                config = json.load(f)
                config.update(data)
                f.truncate(0)
                json.dump(config, f, indent=4, ensure_ascii=False)
            return Response(status=202)
        except:
            return Response(status=403)
