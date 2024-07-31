from flask import Blueprint, Response, send_from_directory, request
import json
import sys
import os


Apex = Blueprint("Apex", __name__)


@Apex.route("assets/<path:filepath>")
def Apex_Assets(**kwargs):
    filepath = kwargs["filepath"]
    fullpath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("apex", "assets", filepath))
    return send_from_directory(*os.path.split(fullpath))


@Apex.route("config", methods=["GET", "POST"])
def Apex_Config():
    configPath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("cfg", "cfg.json"))

    if(not configPath or not os.path.exists(configPath)): return Response(status=404)

    if(request.method == "GET"):
        return send_from_directory(*os.path.split(configPath))

    if(request.method == "POST"):
        try:
            try: data = request.get_json(force=True)
            except: return Response(status=422)

            # make sure the apex cfg path is correct
            if(not os.path.exists(data.get("path", ""))): return Response(status=404)

            # make sure all entries exists
            entries = ["tap", "walk", "jump", "rope", "missing"]
            for key in entries: data[key] = data.get(key, True)

            # create the .cfg file
            with open(os.path.join(data["path"], "ApexGunControl.cfg"), "w") as f:
                if(data["tap"]):
                    f.write(f"bind_US_standard \"{os.environ['KEY_SHOOTING']}\" \"+fixed;+hidden;+attack\"\n")
                if(data["walk"] or data["jump"] or data["rope"]):
                    keycmdrf = {
                        "walk": "+forward",
                        "jump": "+jump",
                        "rope": "+use",
                    }
                    commands = ";".join([keycmdrf[key] for key in keycmdrf if data[key]])
                    f.write(f"bind_US_standard \"{os.environ['KEY_MOVEMENT']}\" \"+fixed;+hidden;{commands}\"\n")

            # create missing default .cfg
            if(data["missing"]):
                defaultCFGs = sys.modules["StorageManager"].LocalStorage.path(os.path.join("apex", "cfg"))
                for file in os.listdir(defaultCFGs):
                    with open(os.path.join(defaultCFGs, file), "r") as org,\
                         open(os.path.join(data["path"], file), "w") as new:
                        new.write(org.read())

            # save the cfg setting
            with open(configPath, "a+") as f:
                f.seek(0)
                config = json.load(f)
                config.update(data)
                f.truncate(0)
                json.dump(config, f, indent=4, ensure_ascii=False)
            return Response(status=202)
        except:
            return Response(status=403)
