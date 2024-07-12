import time
import os

from .Monitor import GameMonitor

import keyboard

import win32con
import win32api

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

class GameController:
    thread = None

    ControlIndex = 0
    ShootingKey = 'p'

    MovementKey = 'o'

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            while(os.environ["USER"] and GameMonitor.focused and GameMonitor.inGame):
                if(win32api.GetAsyncKeyState(0x1) & 0x8000 > 0):
                    keyboard.send(cls.ShootingKey, do_press=True, do_release=False)
                    if(GameMonitor.weaponConfig and GameMonitor.weaponConfig.get("tap", False)):
                        keyboard.send(cls.ShootingKey, do_press=False, do_release=True)
                    recoil = GameMonitor.weaponConfig.get("recoil", [[0, 0], [0, 0]])
                    if(win32api.GetAsyncKeyState(0x2) & 0x8000 > 0):
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, recoil[cls.ControlIndex][0], recoil[cls.ControlIndex][1], 0, 0)
                    cls.ControlIndex = (cls.ControlIndex+1) % len(recoil)
                else:
                    cls.ControlIndex = 0
                    keyboard.send(cls.ShootingKey, do_press=False, do_release=True)
                if(win32api.GetAsyncKeyState(0x5) & 0x8000 > 0):
                    keyboard.send(cls.MovementKey, do_press=True, do_release=True)
                time.sleep(0.001)
            cls.ControlIndex = 0
            keyboard.send(cls.ShootingKey, do_press=False, do_release=True)
