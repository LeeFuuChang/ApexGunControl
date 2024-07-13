import time
import json
import sys
import os

from .Monitor import GameMonitor

import keyboard

import win32con
import win32api

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

class GameController:
    thread = None

    recoilIndex = 0
    recoilMultiplier = 1

    @classmethod
    def controlRunning(cls):
        return os.environ["USER"] and GameMonitor.isFocused and GameMonitor.inGame

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            if(cls.controlRunning()):
                settingsPath = sys.modules["StorageManager"].LocalStorage().path(os.path.join("cfg", "settings.json"))
                with open(settingsPath, "r") as f: settings = json.load(f)
                cls.recoilIndex = 0
                cls.recoilMultiplier = 5.0 / float(settings["sensitivity"] or "5.0")

            while(cls.controlRunning()):
                if(win32api.GetAsyncKeyState(0x1) & 0x8000 > 0):
                    keyboard.send(os.environ["KEY_SHOOTING"], do_press=True, do_release=False)
                    if(GameMonitor.weaponConfig and GameMonitor.weaponConfig.get("tap", False)):
                        keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
                    recoil = GameMonitor.weaponConfig.get("recoil", [[0, 0], [0, 0]])
                    if(win32api.GetAsyncKeyState(0x2) & 0x8000 > 0):
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_MOVE,
                            round(recoil[cls.recoilIndex][0]*cls.recoilMultiplier),
                            round(recoil[cls.recoilIndex][1]*cls.recoilMultiplier),
                        )
                    cls.recoilIndex = (cls.recoilIndex+1) % len(recoil)
                else:
                    cls.recoilIndex = 0
                    keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
                if(win32api.GetAsyncKeyState(0x5) & 0x8000 > 0):
                    keyboard.send(os.environ["KEY_MOVEMENT"], do_press=True, do_release=True)
                time.sleep(0.001)
            else:
                cls.recoilIndex = 0
                cls.recoilMultiplier = 1
                keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
