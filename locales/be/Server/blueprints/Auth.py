from flask import Blueprint, request
from datetime import datetime
from pytz import timezone
import requests as rq
import sys
import os


Auth = Blueprint("Auth", __name__)


os.environ["USERNAME"] = "" if("--debug" not in sys.argv)else "debug@gmail.com"
os.environ["PASSWORD"] = "" if("--debug" not in sys.argv)else "debug"
os.environ["EXPIRE_AT"] = "" if("--debug" not in sys.argv)else "9999/12/31 23:59:59"


@Auth.route("/login", methods=["POST"])
def Auth_Login():
    res = rq.post(
        f"{os.environ['SERVER_URL']}/Login",
        data={
            "username": request.form.get("username", ""),
            "password": request.form.get("password", ""),
        })

    try: 
        data = res.json()
        if( "username" in data and
            "password" in data and
            "expireAt" in data):
            os.environ["USERNAME"]  = data["username"]
            os.environ["PASSWORD"]  = data["password"]
            os.environ["EXPIRE_AT"] = data["expireAt"]
    except: pass

    return {
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "expireAt": os.environ["EXPIRE_AT"],
    }, res.status_code


@Auth.route("/activate", methods=["POST"])
def Auth_Activate():
    res = rq.post(
        f"{os.environ['SERVER_URL']}/Activate",
        data={
            "username": os.environ["USERNAME"],
            "password": os.environ["PASSWORD"],
            "pin"     : request.form.get("pin", ""),
        })

    try: 
        data = res.json()
        if( "username" in data and
            "password" in data and
            "expireAt" in data):
            os.environ["USERNAME"]  = data["username"]
            os.environ["PASSWORD"]  = data["password"]
            os.environ["EXPIRE_AT"] = data["expireAt"]
    except: pass

    return {
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "expireAt": os.environ["EXPIRE_AT"],
    }, res.status_code


@Auth.route("/logout", methods=["POST"])
def Auth_Logout():
    user = {
        "username": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"],
        "expireAt": os.environ["EXPIRE_AT"],
    }
    os.environ["USERNAME"] = ""
    os.environ["PASSWORD"] = ""
    os.environ["EXPIRE_AT"] = ""
    return user, 200


@Auth.route("/expiration", methods=["POST"])
def Auth_Expiration():
    if(not os.environ["EXPIRE_AT"]): return ""
    now = datetime.now(tz=timezone(os.environ["TIMEZONE"]))
    authorized = os.environ["EXPIRE_AT"] > now.strftime(r"%Y/%m/%d %H:%M:%S")
    return os.environ["EXPIRE_AT"] if(authorized)else ""
