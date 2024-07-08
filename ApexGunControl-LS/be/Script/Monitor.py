import threading
import time

from .Detector import WeaponDetector



class GameMonitor:
    thread = None

    weapon = [ None, 0 ]

    @staticmethod
    def update():
        while(not time.sleep(.5)):
            GameMonitor.weapon = WeaponDetector.detect()



if(GameMonitor.thread is None):
    GameMonitor.thread = threading.Thread(target=GameMonitor.update, daemon=True)
    GameMonitor.thread.start()


