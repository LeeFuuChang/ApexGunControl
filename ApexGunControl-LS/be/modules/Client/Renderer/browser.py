from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5 import QtCore, QtGui

import logging
logger = logging.getLogger()
import os

from PackageManager import getPackage
StorageManager = getPackage("StorageManager", os.environ["STORAGE_URL"])
LocalStorage = getattr(StorageManager, "LocalStorage").getInstance()



class BrowserWindow(QWebEngineView):
    closeSignal = QtCore.pyqtSignal()

    minimizeSignal = QtCore.pyqtSignal()

    resizeSignal = QtCore.pyqtSignal(int, int)

    showSignal = QtCore.pyqtSignal()

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

        self.icon = QtGui.QIcon(LocalStorage.path(os.path.join("logo", "Filled.png")))

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

        self.closeSignal.connect(self.close)
        self.minimizeSignal.connect(self.showMinimized)
        self.resizeSignal.connect(self.resize)
        self.showSignal.connect(self.show)

        self.centralize()


    def eventFilter(self, object, event):
        if(object.parent() == self and event.type() == QtCore.QEvent.MouseMove):
            self.mouseMoveEvent(event)
        if(object.parent() == self and event.type() == QtCore.QEvent.MouseButtonPress):
            self.mousePressEvent(event)
        if(object.parent() == self and event.type() == QtCore.QEvent.MouseButtonRelease):
            self.mouseReleaseEvent(event)
        return False


    def mousePressEvent(self, event):
        self.dragging = ((event.buttons() == QtCore.Qt.LeftButton) and (event.y() < self.height()*0.08))
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
        super().resize(w, h)
        self.centralize()


    def connect(self, server, host, port):
        self.server = server
        # self.server.registerAppControl("app-control-close", self.closeSignal.emit)
        # self.server.registerAppControl("app-control-hide", self.minimizeSignal.emit)
        # self.server.registerAppControl("app-control-resize", self.resizeSignal.emit)
        # self.server.registerAppControl("app-control-show", self.showSignal.emit)
        # self.load(QtCore.QUrl(f"http://{host}:{port}/ui"))
        self.load(QtCore.QUrl("http://www.google.com"))
        self.centralize()
