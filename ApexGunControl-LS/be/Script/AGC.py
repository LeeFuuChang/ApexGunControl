from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

import contextlib
import threading
import json
import sys
import os

from .Controller import GameController
from .Monitor import GameMonitor



class ApexGunControl(QWidget):
    padding = 16
    sizeUnit = 32

    toggleStatusWindowSignal = pyqtSignal(bool)

    config = {}

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowIcon(QIcon(os.environ["ICON_PATH"]))
        self.setWindowFlags(Qt.Window|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.toggleStatusWindowSignal.connect(self.setVisible)

        self.setupUI()


    def setupUI(self):
        self.iconLabels = []

        self.firingLabel = QLabel(self)
        self.iconLabels.append(self.firingLabel)

        self.aimingLabel = QLabel(self)
        self.iconLabels.append(self.aimingLabel)

        self.movingLabel = QLabel(self)
        self.iconLabels.append(self.movingLabel)

        self.focusingLabel = QLabel(self)
        self.iconLabels.append(self.focusingLabel)

        self.authorizedLabel = QLabel(self)
        self.iconLabels.append(self.authorizedLabel)

        self.resize(
            self.padding + self.sizeUnit*len(self.iconLabels) + self.padding*len(self.iconLabels),
            self.padding + self.sizeUnit + self.sizeUnit + self.padding
        )

        for i in range(len(self.iconLabels)):
            self.iconLabels[i].setGeometry(self.padding + self.sizeUnit*i + self.padding*i, self.padding, self.sizeUnit, self.sizeUnit)
            self.iconLabels[i].show()

        stretch = int((self.width() - self.padding - self.padding) / 2)

        self.weaponLabel = QLabel(self)
        self.weaponLabel.setAlignment(Qt.AlignVCenter|Qt.AlignLeft)
        self.weaponLabel.setGeometry(self.padding, self.padding + self.sizeUnit, stretch, self.sizeUnit)
        self.weaponLabel.setText("None")
        self.weaponLabel.show()

        self.confidenceLabel = QLabel(self)
        self.confidenceLabel.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.confidenceLabel.setGeometry(self.padding + stretch, self.padding + self.sizeUnit, stretch, self.sizeUnit)
        self.confidenceLabel.setText("0%")
        self.confidenceLabel.show()


    @staticmethod
    def setStateIcon(label: QLabel, name: str, state: bool):
        path = os.path.join("assets", f"{name.capitalize()}-{str(bool(state))[0]}.png")
        icon = QPixmap(sys.modules["StorageManager"].LocalStorage.path(path))
        with contextlib.suppress(RuntimeError):
            label.setPixmap(icon.scaled(label.width(), label.height()))

    def setFiring(self, boolean):
        self.setStateIcon(self.firingLabel, "Firing", boolean)

    def setAiming(self, boolean):
        self.setStateIcon(self.aimingLabel, "Aiming", boolean)

    def setMoving(self, boolean):
        self.setStateIcon(self.movingLabel, "Moving", boolean)

    def setAuthorized(self, boolean):
        self.setStateIcon(self.authorizedLabel, "Authorized", boolean)

    def setFocusing(self, boolean):
        self.setStateIcon(self.focusingLabel, "Focusing", boolean)
        if(not boolean): return
        configRelPath = os.path.join("cfg", "settings.json")
        configAbsPath = sys.modules["StorageManager"].LocalStorage.path(configRelPath)
        with open(configAbsPath, "r") as f: self.config = json.load(f)

    def setWeapon(self, data):
        color = "#E7C975" if(round(data[1]*100)>=int(self.config.get("confidence", "80")))else "#FF0253"
        with contextlib.suppress(RuntimeError):
            self.weaponLabel.setText(str(data[0]))
            self.weaponLabel.setStyleSheet(f"font-size: {int(self.sizeUnit/2)}px; font-weight: 600; color: {color}")
            self.confidenceLabel.setText(f"{round(data[1]*100)}%")
            self.confidenceLabel.setStyleSheet(f"font-size: {int(self.sizeUnit/2)}px; font-weight: 600; color: {color}")


    def showEvent(self, event):
        wg = self.geometry()
        sg = QDesktopWidget().screenGeometry()
        self.move(int((sg.width()-wg.width())/2), 0)
        return super().showEvent(event)


    def run(self):
        if(GameController.thread is None):
            GameController.thread = threading.Thread(target=GameController.update, args=(self, ), daemon=True)
            GameController.thread.start()
        if(GameMonitor.thread is None):
            GameMonitor.thread = threading.Thread(target=GameMonitor.update, args=(self, ), daemon=True)
            GameMonitor.thread.start()
        return self
