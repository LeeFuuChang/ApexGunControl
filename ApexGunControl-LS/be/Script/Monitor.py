from mss import mss
import logging
import time
import json
import sys
import os

from .Detector import WeaponDetector

class GameMonitor:
    mss = None

    storage = sys.modules["StorageManager"].LocalStorage()

    thread = None

    inGame = True

    weaponConfidence = 0.75
    weapon = [ None, 0 ]
    weaponConfig = {}

    @classmethod
    def log(cls, message):
        logging.getLogger().info(f"[{cls.__name__}] {message}")

    @classmethod
    def update(cls):
        cls.mss = mss()
        WeaponDetector.mss = cls.mss
        while(not time.sleep(.5)):
            if(not os.environ["USER"]): continue

            # InGame Detection
            if(not cls.inGame): continue

            # Weapon Detection
            weapon = WeaponDetector.detect()
            if(weapon[0] != cls.weapon[0]):
                cls.log(f"Weapon changed ({cls.weapon} -> {weapon})")
                cls.weapon = weapon
                cls.weaponConfig = {}
                if(weapon[1] > cls.weaponConfidence):
                    weaponConfigPath = cls.storage.path(os.path.join("cfg", "weapons", f"{cls.weapon[0]}.json"))
                    if(os.path.exists(weaponConfigPath)):
                        with open(weaponConfigPath, "r") as f:
                            cls.weaponConfig = json.load(f)