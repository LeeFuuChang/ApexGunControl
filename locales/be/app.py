from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QEvent, QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QIcon

import threading
import traceback
import waitress
import logging
import ctypes
import sys
import os

from Server.Flask import WebServer



class WebRenderer(QWebEngineView):
    closeSignal = pyqtSignal()

    minimizeSignal = pyqtSignal()

    resizeSignal = pyqtSignal(int, int)

    showSignal = pyqtSignal()

    dragging = False
    draggableTop = 0.05
    mouseLastPosition = None

    def __init__(self, *args, **kwargs):
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)

        super(self.__class__, self).__init__(*args, **kwargs)

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowIcon(QIcon(os.environ["ICON_PATH"]))
        self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.page().setBackgroundColor(Qt.transparent)
        self.setAutoFillBackground(True)
        self.setContextMenuPolicy(Qt.NoContextMenu)

        QApplication.instance().installEventFilter(self)
        self.setMouseTracking(True)

        self.closeSignal.connect(self.close)
        self.minimizeSignal.connect(self.showMinimized)
        self.resizeSignal.connect(self.resize)
        self.showSignal.connect(self.show)


    def eventFilter(self, object, event):
        if(object.parent() == self and event.type() == QEvent.MouseMove):
            self.mouseMoveEvent(event)
        if(object.parent() == self and event.type() == QEvent.MouseButtonPress):
            self.mousePressEvent(event)
        if(object.parent() == self and event.type() == QEvent.MouseButtonRelease):
            self.mouseReleaseEvent(event)
        return False


    def mousePressEvent(self, event):
        self.dragging = ((event.buttons() == Qt.LeftButton) and (event.y() < self.height()*self.draggableTop))
        return super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        self.dragging = False
        return super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        if((event.buttons() == Qt.LeftButton) and self.dragging and self.mouseLastPosition):
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
        super().resize(w, h)
        self.centralize()
        self.show()


    def show(self):
        if self.windowState() == Qt.WindowMinimized:
            self.setWindowState(Qt.WindowNoState)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        super().show()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        super().show()


    def connect(self, server, host, port):
        server.registerAppControl("app-control-close", self.closeSignal.emit)
        server.registerAppControl("app-control-minimize", self.minimizeSignal.emit)
        server.registerAppControl("app-control-resize", self.resizeSignal.emit)
        server.registerAppControl("app-control-show", self.showSignal.emit)
        self.load(QUrl(f"http://{host}:{port}/ui"))
        self.centralize()



def run():
    os.environ["ICON_PATH"] = sys.modules["StorageManager"].LocalStorage.path("fe", "assets", "logo", "filled.png")

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

    try:
        logging.info(f"Setting AppUserID to: '{os.environ['APP_USER_MODEL_ID']}'")
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(os.environ["APP_USER_MODEL_ID"])
    except Exception as e:
        logging.error(f"Failed to set AppUserID:\n{''.join(traceback.format_exception(e.__class__, e, e.__traceback__))}")

    qapp = QApplication([*sys.argv, "--ignore-gpu-blocklist"])

    browserWindow = WebRenderer()
    browserWindow.connect(server, server.host, server.port)
    browserWindow.show()

    from Script.Selector import RegionSelector
    regionSelector = RegionSelector(browserWindow)
    server.registerAppControl("app-control-region", regionSelector.showSignal.emit)

    from Script.AGC import ApexGunControl
    script = ApexGunControl(browserWindow)
    script.run()

    sys.exit(qapp.exec_())
