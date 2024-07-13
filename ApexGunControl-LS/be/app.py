import threading
import waitress
import logging
import json
import sys
import os

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5 import QtCore, QtGui

from Script.Detector import WeaponDetector
from Script.Selector import RegionSelector

from Server import WebServer

from Script.Controller import GameController
from Script.Monitor import GameMonitor



class WebRenderer(QWebEngineView):
    closeSignal = QtCore.pyqtSignal()

    minimizeSignal = QtCore.pyqtSignal()

    resizeSignal = QtCore.pyqtSignal(int, int)

    regionSignal = QtCore.pyqtSignal()

    authChangedSignal = QtCore.pyqtSignal(object)

    dragging = False
    mouseLastPosition = None

    def __init__(self, *args, **kwargs):
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)

        super(self.__class__, self).__init__(*args, **kwargs)

        self.icon = QtGui.QIcon(sys.modules["StorageManager"].LocalStorage().path(os.path.join("logo", "Filled.png")))

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowIcon(self.icon)
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowMinMaxButtonsHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.page().setBackgroundColor(QtCore.Qt.transparent)
        self.setAutoFillBackground(True)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        QApplication.instance().installEventFilter(self)
        self.setMouseTracking(True)

        self.server = None

        self.regionSelector = RegionSelector(self)

        self.closeSignal.connect(self.close)
        self.minimizeSignal.connect(self.showMinimized)
        self.resizeSignal.connect(self.resize)
        self.regionSignal.connect(self.selectWeaponDetectRegion)
        self.authChangedSignal.connect(self.authStateChanged)


    def eventFilter(self, object, event):
        if(object.parent() == self and event.type() == QtCore.QEvent.MouseMove):
            self.mouseMoveEvent(event)
        if(object.parent() == self and event.type() == QtCore.QEvent.MouseButtonPress):
            self.mousePressEvent(event)
        if(object.parent() == self and event.type() == QtCore.QEvent.MouseButtonRelease):
            self.mouseReleaseEvent(event)
        return False


    def mousePressEvent(self, event):
        self.dragging = ((event.buttons() == QtCore.Qt.LeftButton) and (event.y() < self.height()*0.05))
        return super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        self.dragging = False
        return super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        if((event.buttons() == QtCore.Qt.LeftButton) and self.dragging and self.mouseLastPosition):
            self.move(self.pos() + event.globalPos() - self.mouseLastPosition)
        self.mouseLastPosition = event.globalPos()
        return super().mouseMoveEvent(event)


    def centralize(self):
        wg = self.geometry()
        sg = QDesktopWidget().availableGeometry()
        self.move(int((sg.width()-wg.width())/2), int((sg.height()-wg.height())/2))


    def resize(self, w, h):
        if((self.width(), self.height()) == (w, h)): return
        logging.getLogger().info(f"Browser Scaled to ({w}, {h})")
        super().resize(w, h)
        self.centralize()
        self.show()


    def selectWeaponDetectRegion(self):
        self.regionSelector.show()


    def authStateChanged(self, user):
        os.environ["USER"] = str(user if(user)else "")
        prettified = json.dumps(user if(user)else {}, indent=4, ensure_ascii=False)
        logging.getLogger().info(f"AuthStateChanged: {prettified}")


    def connect(self, server, host, port):
        self.server = server
        self.server.registerAppControl("app-control-close", self.closeSignal.emit)
        self.server.registerAppControl("app-control-minimize", self.minimizeSignal.emit)
        self.server.registerAppControl("app-control-resize", self.resizeSignal.emit)
        self.server.registerAppControl("app-control-region", self.regionSignal.emit)
        self.server.registerAppControl("app-control-auth", self.authChangedSignal.emit)
        self.load(QtCore.QUrl(f"http://{host}:{port}/ui"))
        logging.getLogger().info(f"Browser Listening on 'http://{host}:{port}/ui'")
        self.centralize()



def run():
    app = QApplication([*sys.argv, "--ignore-gpu-blocklist"])

    server = WebServer()

    threading.Thread(target=waitress.serve, daemon=True, kwargs={
        "app": server,
        "host": server.host, 
        "port": server.port,
        "threads": 8,
    }).start()

    browserWindow = WebRenderer()
    browserWindow.connect(server, server.host, server.port)

    os.environ["KEY_SHOOTING"] = "f5"
    os.environ["KEY_MOVEMENT"] = "f6"

    if(GameController.thread is None):
        GameController.thread = threading.Thread(target=GameController.update, daemon=True)
        GameController.thread.start()

    if(GameMonitor.thread is None):
        GameMonitor.thread = threading.Thread(target=GameMonitor.update, daemon=True)
        GameMonitor.thread.start()

    sys.exit(app.exec_())


