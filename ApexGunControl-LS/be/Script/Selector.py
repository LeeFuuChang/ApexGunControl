import os

from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget, QLabel, QShortcut, QSizeGrip
from PyQt5.QtCore import Qt, QPoint, QEvent, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon

from .Detector import Detector



class RegionSelector(QWidget):
    region2geometry = staticmethod(lambda r : tuple([int(_) for _ in [r[0], r[1], r[2]-r[0], r[3]-r[1]]]))
    geometry2region = staticmethod(lambda g : tuple([int(_) for _ in [g[0], g[1], g[0]+g[2], g[1]+g[3]]]))

    showSignal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowIcon(QIcon(os.environ["ICON_PATH"]))
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(True)

        QShortcut(QKeySequence("ESC"), self).activated.connect(self.close)
        self.closeHint = QLabel(self)
        self.closeHint.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.closeHint.setFixedHeight(16)
        self.closeHint.setText("[ E S C ]")
        self.closeHint.setStyleSheet("font-size: 12px; color: #FFFFFF; background: #FF0000; padding: 0 4px")
        self.closeHint.show()

        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.setStyleSheet("background-color: #FF0000")
            grip.resize(16, 16)
            grip.show()
            self.grips.append(grip)
        self.farestGrip = None

        self.showSignal.connect(self.show)

        QApplication.instance().installEventFilter(self)


    def showEvent(self, event):
        if(Detector is not None):
            Detector.load()
            self.updateRegion()
            self.setGeometry(*self.region2geometry(Detector.region))
        return super().showEvent(event)


    def closeEvent(self, event):
        if(Detector is not None):
            self.updateRegion()
            self.setGeometry(*self.region2geometry(Detector.region))
            Detector.save()
        return super().closeEvent(event)


    def eventFilter(self, object, event):
        if(object.parent() == self and event.type() == QEvent.MouseButtonPress):
            self.mousePressEvent(event)
        if(object.parent() == self and event.type() == QEvent.MouseButtonRelease):
            self.mouseReleaseEvent(event)
        return False


    def mousePressEvent(self, event):
        if(event.buttons() & Qt.LeftButton):
            def dist(grip):
                gripWindowPos = grip.mapTo(grip.window(), grip.rect().center())
                return (gripWindowPos - event.windowPos()).manhattanLength()
            self.farestGrip = max(self.grips, key=dist)
        event.accept()


    def mouseReleaseEvent(self, event):
        if(event.buttons() & Qt.LeftButton and self.farestGrip):
            self.farestGrip = None
        event.accept()


    def updateRegion(self):
        sg = QDesktopWidget().screenGeometry()
        wg = self.geometry()

        x = max(wg.x(), sg.x(), 0)
        y = max(wg.y(), sg.y(), 0)
        w = min(wg.width(), sg.width()-x)
        h = min(wg.height(), sg.height()-y)

        nw = min(h*3, w, sg.width())
        nh = min(w/3, h, sg.height())
        nx = min(max(Detector.region[0], sg.x()), sg.x()+sg.width()-nw)
        ny = min(max(Detector.region[1], sg.y()), sg.y()+sg.height()-nh)

        if(self.grips[0] == self.farestGrip):
            nx = Detector.region[0]
            ny = Detector.region[1]
        if(self.grips[1] == self.farestGrip):
            nx = Detector.region[2] - nw
            ny = Detector.region[1]
        if(self.grips[2] == self.farestGrip):
            nx = Detector.region[2] - nw
            ny = Detector.region[3] - nh
        if(self.grips[3] == self.farestGrip):
            nx = Detector.region[0]
            ny = Detector.region[3] - nh

        Detector.region = self.geometry2region((nx, ny, nw, nh))


    def resizeEvent(self, event):
        if(self.farestGrip): self.updateRegion()

        self.setGeometry(*self.region2geometry(Detector.region))

        w = self.width()
        h = self.height()

        lt = QPoint(     0,      0)
        rt = QPoint(w - 16,      0)
        rb = QPoint(w - 16, h - 16)
        lb = QPoint(     0, h - 16)

        self.grips[0].move(lt)
        self.grips[1].move(rt)
        self.grips[2].move(rb)
        self.grips[3].move(lb)

        self.closeHint.move(int((w-self.closeHint.width())/2), 0)

        return super().resizeEvent(event)


