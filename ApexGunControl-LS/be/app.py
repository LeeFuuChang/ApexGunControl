import threading
import waitress
import sys

from PyQt5.QtWidgets import QApplication

from modules import Client



def run():
    app = QApplication([*sys.argv, "--ignore-gpu-blocklist"])

    server = Client.Server.Server()

    threading.Thread(target=waitress.serve, daemon=True, kwargs={
        "app": server,
        "host": server.host, 
        "port": server.port,
    }).start()

    browserWindow = Client.Renderer.BrowserWindow()
    browserWindow.connect(server, server.host, server.port)
    browserWindow.show()

    sys.exit(app.exec_())