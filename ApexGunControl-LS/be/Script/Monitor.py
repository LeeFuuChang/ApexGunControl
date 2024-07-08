import threading
import logging
import time
import os

from .Detector import WeaponDetector



class GameMonitor:
    thread = None

    weaponConfidence = 0.75
    weapon = [ None, 0 ]

    @classmethod
    def log(cls, message):
        logging.getLogger().info(f"[{cls.__name__}] {message}")

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            if(not os.environ["USER"]): continue
            weapon = WeaponDetector.detect()
            if(weapon[1] > cls.weaponConfidence):
                if(weapon[0] != cls.weapon[0]):
                    cls.log(f"Weapon changed ({cls.weapon} -> {weapon})")
                    cls.weapon = weapon





if(GameMonitor.thread is None):
    GameMonitor.thread = threading.Thread(target=GameMonitor.update, daemon=True)
    GameMonitor.thread.start()


