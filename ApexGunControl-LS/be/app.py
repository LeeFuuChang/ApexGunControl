import threading
import waitress
import sys

from PyQt5.QtWidgets import QApplication

from Renderer import BrowserWindow
from Server import WebServer



def run():
    app = QApplication([*sys.argv, "--ignore-gpu-blocklist"])

    server = WebServer()

    threading.Thread(target=waitress.serve, daemon=True, kwargs={
        "app": server,
        "host": server.host, 
        "port": server.port,
        "threads": 8,
    }).start()

    browserWindow = BrowserWindow()
    browserWindow.connect(server, server.host, server.port)
    browserWindow.show()

    sys.exit(app.exec_())