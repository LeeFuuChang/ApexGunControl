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

from .Detector import Detector, WeaponDetector



class GameMonitor:
    mss = None

    thread = None

    authorized = False

    isFocused = False

    weapon = [ None, 0 ]
    weaponConfig = {}

    @classmethod
    def update(cls, _AGC):
        cls.mss = mss()
        while(not time.sleep(.5)):
            with contextlib.suppress(RuntimeError):
                _AGC.toggleStatusWindowSignal.emit(cls.authorized and cls.isFocused)

            authorized = os.environ["EXPIRE_AT"] > datetime.now(tz=timezone(os.environ["TIMEZONE"])).strftime(r"%Y/%m/%d %H:%M:%S")
            if(cls.authorized != authorized):
                logging.info(f"[{cls.__name__}] Authorize state changed ({cls.authorized} -> {authorized})")
                cls.authorized = authorized

            _AGC.setFocusing(cls.isFocused)
            _AGC.setAuthorized(cls.authorized)
            _AGC.setWeapon(cls.weapon)

            if(not cls.authorized): continue

            # Focus Check
            isFocused = False
            try:
                focus = win32gui.GetForegroundWindow()
                focusPID = win32process.GetWindowThreadProcessId(focus)[1]
                focusProc = psutil.Process(focusPID)
                focusName = focusProc.name().strip().lower()
                isFocused = focusName.startswith("r5apex")
            except:
                pass
            if(cls.isFocused != isFocused):
                logging.info(f"[{cls.__name__}] Focus state changed ({cls.isFocused} -> {isFocused})")
                cls.isFocused = isFocused
            if(not cls.isFocused): continue

            screenshot = np.array(cls.mss.grab(Detector.region))

            # Weapon Detection
            result = WeaponDetector.detect(screenshot)
            if(result[1] > (float(_AGC.config.get("confidence", "80"))/100) and result[0] != cls.weapon[0]):
                logging.info(f"[{cls.__name__}] Weapon changed ({cls.weapon} -> {result})")
                cls.weapon = result
                cls.weaponConfig = {}
                weaponConfigPath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("cfg", "weapons", f"{cls.weapon[0]}.json"))
                if(os.path.exists(weaponConfigPath)):
                    with open(weaponConfigPath, "r") as f:
                        cls.weaponConfig = json.load(f)
