import requests as rq
import webbrowser
import logging
import json
import sys
import os

from flask import Blueprint, send_from_directory, request, Response

App = Blueprint("App", __name__)

@App.route("/version", methods=["GET"])
def App_Version():
    return rq.get(f"{os.environ['SERVER_URL']}/Version", params={"current":os.environ["VERSION"]}).json()

@App.route("/external", methods=["POST"])
def App_External():
    try: data = request.get_json(force=True)
    except: data = {}
    if("url" not in data): return Response(status=404)
    webbrowser.open(str(data["url"]))
    return Response(status=202)

@App.route("/validation/<string:category>", methods=["POST"])
def App_Validation(**kwargs):
    category = kwargs["category"]
    result = False
    try: args = request.get_json(force=True)
    except: args = {}
    if(category == "path"):
        target = args.get("target", "")
        exists = os.path.exists(target)
        filtering = [exists, ]
        for method in args.get("methods", "").split(args.get("sep", "|")):
            if(not hasattr(os.path, method)): continue
            filtering.append(getattr(os.path, method)(target))
        result = all(filtering)
    logging.getLogger().info(f"validating: {category} | result: {result}")
    return json.dumps(result)

@App.route("/config/<string:name>", methods=["GET", "POST"])
def App_Config(**kwargs):
    configPath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("cfg", "app", f"{kwargs['name']}.json"))
    if(request.method == "GET"):
        if(not configPath): return Response(status=404)
        return send_from_directory(*os.path.split(configPath))
    elif(request.method == "POST"):
        try: data = request.get_json(force=True)
        except: data = {}
        if(not configPath): return Response(status=404)
        with open(configPath, "a+") as f:
            f.seek(0)
            config = json.load(f)
            config.update(data)
            f.truncate(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
        return Response(status=202)

App.control_functions = {}
@App.route("/controls/<string:name>", methods=["POST"])
def App_Controls(**kwargs):
    name = kwargs["name"]
    if(name not in App.control_functions): return Response(status=404)
    try: data = request.get_json(force=True)
    except: data = []
    for func in App.control_functions[name]: func(*data)
    return Response(status=202)