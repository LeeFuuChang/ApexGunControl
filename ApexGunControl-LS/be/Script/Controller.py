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

    @staticmethod
    def update(_AGC):
        recoilIndex = 0
        recoilMultiplier = 0

        controlRunning = lambda : (
            os.environ["USER"] and 
            GameMonitor.isFocused and 
            GameMonitor.inGame
        )

        while(not time.sleep(.5)):
            _AGC.setFiring(False)
            _AGC.setAiming(False)
            _AGC.setMoving(False)

            if(controlRunning()):
                recoilIndex = 0
                recoilMultiplier = 5.0 / float(_AGC.config.get("sensitivity", "5.0"))

            while(controlRunning()):
                _AGC.setFiring(win32api.GetAsyncKeyState(0x1) & 0x8000 > 0)
                _AGC.setAiming(win32api.GetAsyncKeyState(0x2) & 0x8000 > 0)
                _AGC.setMoving(win32api.GetAsyncKeyState(0x5) & 0x8000 > 0)

                if(win32api.GetAsyncKeyState(0x1) & 0x8000 > 0):
                    keyboard.send(os.environ["KEY_SHOOTING"], do_press=True, do_release=False)
                    if(GameMonitor.weaponConfig and GameMonitor.weaponConfig.get("tap", False)):
                        keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
                    recoil = GameMonitor.weaponConfig.get("recoil", [[0, 0], [0, 0]])
                    if(win32api.GetAsyncKeyState(0x2) & 0x8000 > 0):
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_MOVE,
                            round(recoil[recoilIndex%len(recoil)][0]*recoilMultiplier),
                            round(recoil[recoilIndex%len(recoil)][1]*recoilMultiplier),
                        )
                    recoilIndex = (recoilIndex+1) % len(recoil)
                else:
                    recoilIndex = 0
                    keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)

                if(win32api.GetAsyncKeyState(0x5) & 0x8000 > 0):
                    keyboard.send(os.environ["KEY_MOVEMENT"], do_press=True, do_release=True)

                time.sleep(0.0175)

            keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
