import time
import os

from .Monitor import GameMonitor
from .Listener import Mouse, Keyboard

import pydirectinput
pydirectinput.FAILSAFE = False

import win32con
import win32api

class GameController:
    thread = None

    ControlIndex = 0
    ShootingKey = 'p'

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            while(os.environ["USER"] and GameMonitor.inGame):
                if(Mouse.pressed[Mouse.Button.left]):
                    pydirectinput.keyDown(cls.ShootingKey, _pause=False)
                    if(GameMonitor.weaponConfig and GameMonitor.weaponConfig.get("tap", False)):
                        pydirectinput.keyUp(cls.ShootingKey, _pause=False)
                    recoil = GameMonitor.weaponConfig.get("recoil", [[0, 0], [0, 0]])
                    if(Mouse.pressed[Mouse.Button.right]):
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, recoil[cls.ControlIndex][0], recoil[cls.ControlIndex][1], 0, 0)
                    cls.ControlIndex = (cls.ControlIndex+1) % len(recoil)
                else:
                    cls.ShakeIndex = 0
                    if(Keyboard.pressed[repr(cls.ShootingKey)]):
                        pydirectinput.keyUp(cls.ShootingKey, _pause=False)
                time.sleep(0.0001)
