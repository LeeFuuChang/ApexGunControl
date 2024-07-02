from flask import Flask, redirect
import socket

# for app
from .APP import App
from .UI import Ui



def getRandomPort():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class Server(Flask):
    host = "localhost"
    port = getRandomPort()

    def __init__(self):
        super(self.__class__, self).__init__(__name__)
        self.config["SECRET_KEY"] = "ThisIsNotSnakeCaseWhichShouldBeUsedInPython"

        self.appControls = {}

        self.add_url_rule("/", endpoint="ui", view_func=lambda:redirect("/ui"))
        for bp in [App, Ui, ]:
            name = bp.name.lower() 
            self.blueprints[name] = bp
            self.register_blueprint(bp, url_prefix=f"/{name}")


    def registerAppControl(self, name, func):
        self.blueprints["app"].control_functions[name] = func