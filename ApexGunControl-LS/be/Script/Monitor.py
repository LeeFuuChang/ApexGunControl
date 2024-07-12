from mss import mss
import numpy as np
import logging
import time
import json
import sys
import os

import win32process
import win32gui
import psutil

from .Detector import Detector, InGameDetector, WeaponDetector

class GameMonitor:
    mss = None

    storage = sys.modules["StorageManager"].LocalStorage()

    thread = None

    focused = False

    inGame = False

    confidence = 0.75

    weapon = [ None, 0 ]
    weaponConfig = {}

    @classmethod
    def log(cls, message):
        logging.getLogger().info(f"[{cls.__name__}] {message}")

    @classmethod
    def update(cls):
        cls.mss = mss()
        while(not time.sleep(.5)):
            if(not os.environ["USER"]): continue

            cls.focused = False
            try:
                focus = win32gui.GetForegroundWindow()
                focusPID = win32process.GetWindowThreadProcessId(focus)[1]
                focusName = psutil.Process(focusPID).name().strip().lower()
                cls.focused = focusName.startswith("r5apex")
            except:
                pass
            if(not cls.focused): continue

            screenshot = np.array(cls.mss.grab(Detector.region))

            # InGame Detection
            result = InGameDetector.detect(screenshot)
            foundClue = (result[1] > 0.1 and result[1] > cls.confidence/2)
            newGameCof = 10 if(foundClue)else max(0, cls.inGame - 1)
            if(bool(cls.inGame) != bool(newGameCof)):
                cls.log(f"InGame state changed ({bool(cls.inGame)} -> {bool(newGameCof)})")
            cls.inGame = newGameCof
            if(not cls.inGame): continue

            # Weapon Detection
            result = WeaponDetector.detect(screenshot)
            if(result[1] > cls.confidence and result[0] != cls.weapon[0]):
                cls.log(f"Weapon changed ({cls.weapon} -> {result})")
                cls.weapon = result
                cls.weaponConfig = {}
                weaponConfigPath = cls.storage.path(os.path.join("cfg", "weapons", f"{cls.weapon[0]}.json"))
                if(os.path.exists(weaponConfigPath)):
                    with open(weaponConfigPath, "r") as f:
                        cls.weaponConfig = json.load(f)