from PyQt5.QtWidgets import QWidget, QDesktopWidget, QLabel, QGraphicsColorizeEffect
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor

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

        self.toggleStatusWindowSignal.connect(self.setVisibility)

        self.setupUI()


    def setupUI(self):
        self.iconLabels = []

        self.state_T_Color = QColor("#E7C975")
        self.state_F_Color = QColor("#FF0253")

        self.firingLabel = QLabel(self)
        self.firingLabel.setGraphicsEffect(QGraphicsColorizeEffect())
        self.iconLabels.append(self.firingLabel)

        self.aimingLabel = QLabel(self)
        self.aimingLabel.setGraphicsEffect(QGraphicsColorizeEffect())
        self.iconLabels.append(self.aimingLabel)

        self.movingLabel = QLabel(self)
        self.movingLabel.setGraphicsEffect(QGraphicsColorizeEffect())
        self.iconLabels.append(self.movingLabel)

        self.nadingLabel = QLabel(self)
        self.nadingLabel.setGraphicsEffect(QGraphicsColorizeEffect())
        self.iconLabels.append(self.nadingLabel)

        self.inGameLabel = QLabel(self)
        self.inGameLabel.setGraphicsEffect(QGraphicsColorizeEffect())
        self.iconLabels.append(self.inGameLabel)

        self.resize(
            self.padding + self.sizeUnit*len(self.iconLabels) + self.padding*len(self.iconLabels),
            self.padding + self.sizeUnit + self.sizeUnit + self.padding
        )

        for i in range(len(self.iconLabels)):
            self.iconLabels[i].setGeometry(self.padding + self.sizeUnit*i + self.padding*i, self.padding, self.sizeUnit, self.sizeUnit)
            self.iconLabels[i].show()

        available = self.width() - self.padding*2

        self.weaponLabel = QLabel(self)
        self.weaponLabel.setAlignment(Qt.AlignVCenter|Qt.AlignLeft)
        self.weaponLabel.setGeometry(self.padding, self.padding + self.sizeUnit, available - self.sizeUnit*2, self.sizeUnit)
        self.weaponLabel.setText("None")
        self.weaponLabel.show()

        self.confidenceLabel = QLabel(self)
        self.confidenceLabel.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
        self.confidenceLabel.setGeometry(self.weaponLabel.x()+self.weaponLabel.width(), self.padding + self.sizeUnit, self.sizeUnit*2, self.sizeUnit)
        self.confidenceLabel.setText("0%")
        self.confidenceLabel.show()


    def setStateIcon(self, label: QLabel, name: str, state: bool):
        icon = QPixmap(sys.modules["StorageManager"].LocalStorage.path("assets", f"{name}-{str(bool(state))[0]}.png"))
        color = self.state_T_Color if(bool(state))else self.state_F_Color
        with contextlib.suppress(RuntimeError):
            label.setPixmap(icon.scaled(label.width(), label.height()))
            label.graphicsEffect().setColor(color)

    def setFiring(self, boolean):
        self.setStateIcon(self.firingLabel, "Firing", boolean)

    def setAiming(self, boolean):
        self.setStateIcon(self.aimingLabel, "Aiming", boolean)

    def setMoving(self, boolean):
        self.setStateIcon(self.movingLabel, "Moving", boolean)

    def setNading(self, boolean):
        self.setStateIcon(self.nadingLabel, "Nading", boolean)

    def setInGame(self, boolean):
        self.setStateIcon(self.inGameLabel, "InGame", boolean)

    def setFocusing(self, boolean):
        if(not boolean): return
        configPath = sys.modules["StorageManager"].LocalStorage.path("cfg", "settings.json")
        with open(configPath, "r") as f: 
            try: self.config = json.load(f)
            except: self.config = {}
        self.state_T_Color = QColor(self.config.get("floating-color-1", "#E7C975"))
        self.state_F_Color = QColor(self.config.get("floating-color-2", "#FF0253"))

    def setWeapon(self, data):
        color = self.state_T_Color if(round(data[1]*100)>int(self.config.get("confidence", "80")))else self.state_F_Color
        style = f"font-size: {int(self.sizeUnit/2)}px; font-weight: 600; color: rgba{color.getRgb()}"
        with contextlib.suppress(RuntimeError):
            self.weaponLabel.setText(str(data[0]))
            self.weaponLabel.setStyleSheet(style)
            self.confidenceLabel.setText(f"{round(data[1]*100)}%")
            self.confidenceLabel.setStyleSheet(style)


    def setVisibility(self, boolean):
        self.setVisible(boolean and self.config.get("floating", True))


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
