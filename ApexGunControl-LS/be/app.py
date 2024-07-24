import threading
import waitress
import logging
import sys
import os

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5 import QtCore, QtGui

from Server.Flask import WebServer



class WebRenderer(QWebEngineView):
    closeSignal = QtCore.pyqtSignal()

    minimizeSignal = QtCore.pyqtSignal()

    resizeSignal = QtCore.pyqtSignal(int, int)

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

        iconPath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("fe", "assets", "logo", "filled.png"))

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowIcon(QtGui.QIcon(iconPath))
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowMinMaxButtonsHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.page().setBackgroundColor(QtCore.Qt.transparent)
        self.setAutoFillBackground(True)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        QApplication.instance().installEventFilter(self)
        self.setMouseTracking(True)

        self.server = None

        self.closeSignal.connect(self.close)
        self.minimizeSignal.connect(self.showMinimized)
        self.resizeSignal.connect(self.resize)


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


    def moveEvent(self, event):
        wg = self.geometry()
        sg = QDesktopWidget().screenGeometry()
        self.setGeometry(
            max(0, min(wg.x(), sg.width()-wg.width())),
            max(0, min(wg.y(), sg.height()-wg.height())),
            wg.width(),
            wg.height(),
        )
        return super().moveEvent(event)


    def centralize(self):
        wg = self.geometry()
        sg = QDesktopWidget().screenGeometry()
        self.move(int((sg.width()-wg.width())/2), int((sg.height()-wg.height())/2))


    def resize(self, w, h):
        if((self.width(), self.height()) == (w, h)): return
        logging.info(f"Browser Scaled to ({w}, {h})")
        super().resize(w, h)
        self.centralize()
        self.show()


    def connect(self, server, host, port):
        self.server = server
        self.server.registerAppControl("app-control-close", self.closeSignal.emit)
        self.server.registerAppControl("app-control-minimize", self.minimizeSignal.emit)
        self.server.registerAppControl("app-control-resize", self.resizeSignal.emit)
        self.load(QtCore.QUrl(f"http://{host}:{port}/ui"))
        self.centralize()



def run():
    os.environ["KEY_SHOOTING"] = "f5"
    os.environ["KEY_MOVEMENT"] = "f6"

    server = WebServer()

    if("--server" in sys.argv):
        return server.run(
            host=server.host,
            port=server.port,
            threaded=True,
        )

    threading.Thread(
        target=waitress.serve,
        daemon=True,
        kwargs={
            "app": server,
            "host": server.host,
            "port": server.port,
            "threads": 8,
        }
    ).start()

    qapp = QApplication([*sys.argv, "--ignore-gpu-blocklist"])

    browserWindow = WebRenderer()
    browserWindow.connect(server, server.host, server.port)

    from Script.Selector import RegionSelector
    regionSelector = RegionSelector(browserWindow)
    server.registerAppControl("app-control-region", regionSelector.showSignal.emit)

    from Script.AGC import ApexGunControl
    script = ApexGunControl(browserWindow)
    script.run()

    sys.exit(qapp.exec_())
