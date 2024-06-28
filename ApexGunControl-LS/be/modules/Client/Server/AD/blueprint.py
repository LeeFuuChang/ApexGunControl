from flask import Blueprint, request, Response
import webbrowser
import requests
import random
import os

Ad = Blueprint("Ad", __name__)

@Ad.route("/random", methods=["GET"])
def Ad_Random():
    try: data = requests.get(f"{os.environ['SERVER_URL']}/Ads").json()
    except: data = []
    return {} if(not data)else random.choice(data)

@Ad.route("/visit", methods=["POST"])
def Ad_Visit():
    try: data = request.get_json(force=True)
    except: data = {}
    if("href" not in data): return Response(status=400)
    webbrowser.open(data["href"])
    return Response(status=200)