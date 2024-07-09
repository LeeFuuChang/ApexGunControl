import time
import os

from .Monitor import GameMonitor
from .Listener import Mouse, Keyboard

import pydirectinput
pydirectinput.FAILSAFE = False

class GameController:
    thread = None

    ShootingKey = 'p'

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            while(os.environ["USER"] and GameMonitor.inGame):
                if(GameMonitor.weaponConfig):
                    if(Mouse.pressed[Mouse.Button.left]):
                        pydirectinput.keyDown(cls.ShootingKey, _pause=False)
                        if(GameMonitor.weaponConfig.get("tap", False)):
                            pydirectinput.keyUp(cls.ShootingKey, _pause=False)
                    else:
                        if(Keyboard.pressed[repr(cls.ShootingKey)]):
                            pydirectinput.keyUp(cls.ShootingKey, _pause=False)
                time.sleep(.005)
