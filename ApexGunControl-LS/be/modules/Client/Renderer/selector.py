import json
import sys
import os

from detection import Detector

from PyQt5.QtWidgets import QWidget, QLabel, QShortcut, QSizeGrip
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QKeySequence



class SelectionWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(True)

        self.setMinimumSize(64*3, 64)

        self.region = Detector.defaultR

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


    def showEvent(self, event):
        path = sys.modules["StorageManager"].LocalStorage().path(os.path.join("cfg", "settings.json"))
        with open(path, "r") as f:
            config = json.load(f)
            self.region = (
                int(float(config.get("region-l", self.region[0]))),
                int(float(config.get("region-t", self.region[1]))),
                int(float(config.get("region-r", self.region[2]))),
                int(float(config.get("region-b", self.region[3]))),
            )
        self.resize(self.region[2]-self.region[0], self.region[3]-self.region[1])
        self.move(self.region[0], self.region[1])
        super().showEvent(event)



    def closeEvent(self, event):
        path = sys.modules["StorageManager"].LocalStorage().path(os.path.join("cfg", "settings.json"))
        with open(path, "a+") as f:
            f.seek(0)
            config = json.load(f)
            config.update({
                "region-l": f"{self.region[0]}",
                "region-t": f"{self.region[1]}",
                "region-r": f"{self.region[2]}",
                "region-b": f"{self.region[3]}",
            })
            f.truncate(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
        super().closeEvent(event)


    def mouseMoveEvent(self, event):
        self.farestGrip = max(self.grips, key=lambda g:(g.mapToParent(g.rect().center())-event.pos()).manhattanLength())


    def updateDetect(self):
        res, cof = Detector.detect(self.region, "", 0.8)
        self.detectHint.setText(f"{res} - {round(cof*100)}%")


    def updateRegion(self):
        rect = self.geometry()
        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()

        nw = min(h*3, w)
        nh = min(w/3, h)

        if(self.grips[0] == self.farestGrip):
            self.region = (x, y, x+nw, y+nh)
        if(self.grips[1] == self.farestGrip):
            self.region = (x+w-nw, y, x+w, y+nh)
        if(self.grips[2] == self.farestGrip):
            self.region = (x+w-nw, y+h-nh, x+w, y+h)
        if(self.grips[3] == self.farestGrip):
            self.region = (x, y+h-nh, x+nw, y+h)

        self.region = tuple([int(_) for _ in self.region])

        self.setGeometry(self.region[0], self.region[1], self.region[2]-self.region[0], self.region[3]-self.region[1])


    def resizeEvent(self, event):
        super().resizeEvent(event)

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

