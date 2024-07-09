import threading
import time
import os

from Monitor import GameMonitor
from Input import Mouse, Keyboard


class Controller:
    thread = None

    ShootingKey = 'p'

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            while(os.environ["USER"] and GameMonitor.inGame and GameMonitor.canShoot):
                if(Mouse.pressed[Mouse.Button.left]):
                    Keyboard.Tap(cls.ShootingKey)



if(Controller.thread is None):
    Controller.thread = threading.Thread(target=Controller.update, daemon=True)
    Controller.thread.start()


