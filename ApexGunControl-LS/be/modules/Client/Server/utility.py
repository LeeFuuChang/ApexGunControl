from flask import Flask
import socket

# for app
from .AD import Ad
from .APP import App
from .CONFIG import Config
from .STORAGE import Storage
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

        self.appBlueprints = {bp.name.lower():bp for bp in [
            # for app
            Ad, App, Config, Storage, Ui, 
        ]}
        for name in self.appBlueprints:
            self.blueprints[name] = self.appBlueprints[name]
            self.register_blueprint(self.appBlueprints[name], url_prefix=f"/{name}")


    def registerAppControl(self, name, func):
        self.blueprints["app"].control_functions[name] = func