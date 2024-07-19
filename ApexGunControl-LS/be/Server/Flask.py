from flask import Flask, redirect
import logging
import socket
import os

from .blueprints.Ui import Ui
from .blueprints.App import App
from .blueprints.Apex import Apex



def getRandomPort():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class WebServer(Flask):
    host = "localhost"
    port = getRandomPort()

    def __init__(self):
        super(self.__class__, self).__init__(__name__)
        self.config["SECRET_KEY"] = "ThisIsNotSnakeCaseWhichShouldBeUsedInPython"

        os.environ["USERNAME"] = ""
        os.environ["PASSWORD"] = ""
        os.environ["EXPIRE_AT"] = ""

        self.appControls = {}

        self.add_url_rule("/", endpoint="ui", view_func=lambda:redirect("/ui"))
        for bp in [Ui, App, Apex, ]:
            name = bp.name.lower() 
            self.blueprints[name] = bp
            self.register_blueprint(bp, url_prefix=f"/{name}")

        logging.getLogger().info(f"Server Initlized on ({self.host}, {self.port})")


    def registerAppControl(self, name, func):
        self.blueprints["app"].control_functions[name] = func