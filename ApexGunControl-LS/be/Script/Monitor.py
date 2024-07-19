from datetime import datetime
from pytz import timezone
from mss import mss
import numpy as np
import contextlib
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

    thread = None

    authorized = False

    isFocused = False

    inGame = False

    weapon = [ None, 0 ]
    weaponConfig = {}

    @classmethod
    def log(cls, message):
        logging.getLogger().info(f"[{cls.__name__}] {message}")

    @classmethod
    def update(cls, _AGC):
        cls.mss = mss()
        while(not time.sleep(.5)):
            now = datetime.now(tz=timezone("Asia/Taipei"))

            cls.authorized = os.environ["EXPIRE_AT"] > now.strftime(r"%Y/%m/%d %H:%M:%S")

            with contextlib.suppress(RuntimeError):
                _AGC.toggleStatusWindowSignal.emit(cls.authorized and cls.isFocused)

            if(not cls.authorized): continue

            _AGC.setFocusing(cls.isFocused)
            _AGC.setMatching(cls.isFocused and cls.inGame)
            _AGC.setWeapon(cls.weapon)

            # Focus Check
            isFocused = False
            try:
                focus = win32gui.GetForegroundWindow()
                focusPID = win32process.GetWindowThreadProcessId(focus)[1]
                focusProc = psutil.Process(focusPID)
                focusName = focusProc.name().strip().lower()
                isFocused = focusName.startswith("r5apex") or focusPID == os.getpid()
            except:
                pass
            if(cls.isFocused != isFocused):
                cls.log(f"Focus state changed ({cls.isFocused} -> {isFocused})")
                cls.isFocused = isFocused
            if(not cls.isFocused): continue

            screenshot = np.array(cls.mss.grab(Detector.region))

            # InGame Detection
            result = InGameDetector.detect(screenshot)
            foundClue = (result[1] > 0.1 and result[1] > (float(_AGC.config.get("confidence", "80"))/250))
            newGameCof = 3 if(foundClue)else max(0, cls.inGame - 1)
            if(bool(cls.inGame) != bool(newGameCof)):
                cls.log(f"InGame state changed ({bool(cls.inGame)} -> {bool(newGameCof)})")
            cls.inGame = newGameCof
            if(not cls.inGame): continue

            # Weapon Detection
            result = WeaponDetector.detect(screenshot)
            if(result[1] > (float(_AGC.config.get("confidence", "80"))/100) and result[0] != cls.weapon[0]):
                cls.log(f"Weapon changed ({cls.weapon} -> {result})")
                cls.weapon = result
                cls.weaponConfig = {}
                weaponConfigPath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("cfg", "weapons", f"{cls.weapon[0]}.json"))
                if(os.path.exists(weaponConfigPath)):
                    with open(weaponConfigPath, "r") as f:
                        cls.weaponConfig = json.load(f)
