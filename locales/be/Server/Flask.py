from flask import Flask, Response, redirect, request
import traceback
import logging
import socket

from .blueprints.Ui import Ui
from .blueprints.App import App
from .blueprints.Auth import Auth

from .blueprints.Apex import Apex

BLUEPRINTS = [Ui, App, Auth, Apex, ]


def getRandomPort():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class WebServer(Flask):
    host = "localhost"
    port = getRandomPort()

    def registerAppControl(self, name, func):
        self.blueprints["app"].control_functions[name] = func

    def __init__(self):
        super(self.__class__, self).__init__(__name__)
        self.config["TRAP_HTTP_EXCEPTIONS"] = True

        self.appControls = {}

        self.add_url_rule("/", endpoint="ui", view_func=lambda:redirect("/ui"))
        for bp in BLUEPRINTS:
            name = bp.name.lower() 
            self.blueprints[name] = bp
            self.register_blueprint(bp, url_prefix=f"/{name}")

        @self.errorhandler(Exception)
        def handle_error(error):
            if(not hasattr(error, "code") or error.code//100 == 5):
                logging.error(traceback.format_exc())
                return Response(repr(error), 500)
            return Response.force_type(error, request.environ)

        logging.info(f"Server Initlized on ({self.host}, {self.port})")
