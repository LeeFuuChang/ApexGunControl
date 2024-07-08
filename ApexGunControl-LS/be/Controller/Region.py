import os

from PyQt5.QtWidgets import QWidget, QLabel, QShortcut, QSizeGrip
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QKeySequence

from .Monitor import GameMonitor



class SelectionWindow(QWidget):
    region2geometry = staticmethod(lambda r : tuple([int(_) for _ in [r[0], r[1], r[2]-r[0], r[3]-r[1]]]))
    geometry2region = staticmethod(lambda g : tuple([int(_) for _ in [g[0], g[1], g[0]+g[2], g[1]+g[3]]]))

    regionCarrier = None

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(True)

        self.setMinimumSize(64*3, 64)

        QShortcut(QKeySequence("ESC"), self).activated.connect(self.close)
        self.closeHint = QLabel(self)
        self.closeHint.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.closeHint.setFixedHeight(16)
        self.closeHint.setText("[ E S C ]")
        self.closeHint.setStyleSheet("font-size: 12px; color: #FFFFFF; background: #FF0000; padding: 0 4px")
        self.closeHint.show()

        self.detectHint = QLabel(self)
        self.detectHint.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.detectHint.setFixedHeight(16)
        self.detectHint.setText("[ N/A - 0% ]")
        self.detectHint.setStyleSheet("font-size: 12px; color: #FFFFFF; background: #FF0000; padding: 0 4px")
        self.detectHint.show()

        self.detectTimer = QTimer(self)
        self.detectTimer.timeout.connect(self.updateDetect)
        self.detectTimer.start(1000//2)

        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.setStyleSheet("background-color: #FF0000")
            grip.resize(16, 16)
            grip.show()
            self.grips.append(grip)
        self.farestGrip = None

        self.setMouseTracking(True)


    def select(self, carrier):
        self.regionCarrier = carrier
        self.show()


    def showEvent(self, event):
        if(self.regionCarrier is not None):
            self.regionCarrier.load()
            self.setGeometry(*self.region2geometry(self.regionCarrier.region))
        return super().showEvent(event)


    def closeEvent(self, event):
        if(self.regionCarrier is not None):
            self.regionCarrier.save()
            self.regionCarrier = None
        return super().closeEvent(event)


    def mouseMoveEvent(self, event):
        self.farestGrip = max(self.grips, key=lambda g:(g.mapToParent(g.rect().center())-event.pos()).manhattanLength())
        return super().mouseMoveEvent(event)


    def updateDetect(self):
        self.detectHint.setText(f"{GameMonitor.weapon[0]} - {round(GameMonitor.weapon[1]*100)}%")
        self.detectHint.adjustSize()


    def updateRegion(self):
        if(not self.regionCarrier): return

        g = self.geometry()
        x = max(g.x(), self.regionCarrier.monitor["left"])
        y = max(g.y(), self.regionCarrier.monitor["top"])
        w = min(g.width(), self.regionCarrier.monitor["width"]-g.x())
        h = min(g.height(), self.regionCarrier.monitor["height"]-g.y())

        nw = min(h*3, w)
        nh = min(w/3, h)

        if(self.grips[0] == self.farestGrip):
            self.regionCarrier.region = self.geometry2region((x, y, nw, nh))
        if(self.grips[1] == self.farestGrip):
            self.regionCarrier.region = self.geometry2region((x+w-nw, y, w, nh))
        if(self.grips[2] == self.farestGrip):
            self.regionCarrier.region = self.geometry2region((x+w-nw, y+h-nh, w, h))
        if(self.grips[3] == self.farestGrip):
            self.regionCarrier.region = self.geometry2region((x, y+h-nh, nw, h))

        self.setGeometry(*self.region2geometry(self.regionCarrier.region))


    def paintEvent(self, event):
        self.updateRegion()
        return super().paintEvent(event)


    def resizeEvent(self, event):
        self.updateRegion()

        rect = self.geometry()
        w = rect.width()
        h = rect.height()

        lt = QPoint(     0,      0)
        rt = QPoint(w - 16,      0)
        rb = QPoint(w - 16, h - 16)
        lb = QPoint(     0, h - 16)

        self.grips[0].move(lt)
        self.grips[1].move(rt)
        self.grips[2].move(rb)
        self.grips[3].move(lb)

        self.closeHint.move(int((w-self.closeHint.width())/2), 0)
        self.detectHint.move(int((w-self.detectHint.width())/2), h-self.detectHint.height())

        return super().resizeEvent(event)


