from datetime import datetime
from pytz import timezone
import numpy as np
import contextlib
import logging
import time
import json
import mss
import sys
import os

import win32process
import win32gui
import psutil

from .Detector import Detector, InGameDetector, WeaponDetector



class GameMonitor:
    thread = None

    authorized = False

    isFocused = False

    inGame = False

    weapon = [ None, 0 ]
    weaponConfig = {}

    @classmethod
    def update(cls, _AGC):
        with mss.mss() as screen:
            while(not time.sleep(.5)):
                focus = win32gui.GetForegroundWindow()
                focusPID = win32process.GetWindowThreadProcessId(focus)[1]

                with contextlib.suppress(RuntimeError):
                    _AGC.toggleStatusWindowSignal.emit(cls.authorized and (cls.isFocused or focusPID == os.getpid()))

                authorized = os.environ["EXPIRE_AT"] > datetime.now(tz=timezone(os.environ["TIMEZONE"])).strftime(r"%Y/%m/%d %H:%M:%S")
                if(cls.authorized != authorized):
                    logging.info(f"[{cls.__name__}] Authorize state changed ({cls.authorized} -> {authorized})")
                    cls.authorized = authorized

                if(not cls.authorized): continue

                _AGC.setFocusing(cls.isFocused)
                _AGC.setInGame(cls.isFocused and cls.inGame)
                _AGC.setWeapon(cls.weapon)

                # Focus Check
                isFocused = False
                try:
                    focusProc = psutil.Process(focusPID)
                    isFocused = os.path.split(focusProc.exe())[1].startswith("r5apex")
                except:
                    pass
                if(cls.isFocused != isFocused):
                    logging.info(f"[{cls.__name__}] Focus state changed ({cls.isFocused} -> {isFocused})")
                    cls.isFocused = isFocused
                if(not cls.isFocused): continue

                lregion = (0, Detector.region[1], Detector.region[2]-Detector.region[0], Detector.region[3])
                rregion = Detector.region
                screenshot = np.hstack((np.array(screen.grab(lregion)), np.array(screen.grab(rregion))))

                # InGame Detection
                result = InGameDetector.detect(screenshot)
                foundClue = (result[1] > 0.1 and result[1] > (float(_AGC.config.get("confidence", "80"))/100))
                newGameCof = 3 if(foundClue)else max(0, cls.inGame - 1)
                if(bool(cls.inGame) != bool(newGameCof)):
                    logging.info(f"[{cls.__name__}] InGame cof changed ({bool(cls.inGame)} -> {bool(newGameCof)}) [{round(result[1]*100)}%]")
                cls.inGame = newGameCof
                if(not cls.inGame):
                    cls.weapon = [ "InGame", result[1] ]
                    cls.weaponConfig = {}
                    continue

                # Weapon Detection
                result = WeaponDetector.detect(screenshot)
                if(result[0] != cls.weapon[0] and result[1] > (float(_AGC.config.get("confidence", "80"))/100)): # != / >
                    logging.info(f"[{cls.__name__}] Weapon changed ({cls.weapon} -> {result}) [{round(result[1]*100)}%]")
                    cls.weapon = result
                    cls.weaponConfig = {}
                    weaponConfigPath = sys.modules["StorageManager"].LocalStorage.path("cfg", "weapons", f"{cls.weapon[0]}.json")
                    if(os.path.exists(weaponConfigPath)):
                        with open(weaponConfigPath, "r") as f:
                            cls.weaponConfig = json.load(f)
                if(result[0] != cls.weapon[0] and result[1] < (float(_AGC.config.get("confidence", "80"))/100)): # != / <
                    logging.info(f"[{cls.__name__}] Weapon 'maybe' changed ({cls.weapon} -> {result}) [{round(result[1]*100)}%]")
                    cls.weapon = result
                    cls.weaponConfig = {}
                if(result[0] == cls.weapon[0] and result[1] > (float(_AGC.config.get("confidence", "80"))/100)): # == / >
                    cls.weapon = result
                if(result[0] == cls.weapon[0] and result[1] > (float(_AGC.config.get("confidence", "80"))/100)): # == / <
                    cls.weapon = result
