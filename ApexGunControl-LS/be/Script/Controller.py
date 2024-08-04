import time
import os

import keyboard
import win32con
import win32api

import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

from .Monitor import GameMonitor



class GameController:
    thread = None

    @staticmethod
    def update(_AGC):
        recoilIndex = 0
        recoilMultiplier = 0

        controlRunning = lambda : (
            GameMonitor.authorized and 
            GameMonitor.isFocused and 
            GameMonitor.inGame
        )

        grenadeMode = False
        def setGrenadeMode(state):
            nonlocal grenadeMode
            grenadeMode = state and controlRunning()
        keyboard.on_press_key("g", lambda e : setGrenadeMode(1), suppress=False)
        keyboard.on_press_key(("1", "2", "3", "4", "5", "6", "7", "8", "9"), lambda e : setGrenadeMode(0), suppress=False)

        while(not time.sleep(.5)):
            _AGC.setFiring(False)
            _AGC.setAiming(False)
            _AGC.setMoving(False)
            _AGC.setNading(False)

            keyboard.send(os.environ["KEY_MOVEMENT"], do_press=False, do_release=True)
            keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)

            if(controlRunning()):
                recoilIndex = 0
                recoilMultiplier = 5.0 / float(_AGC.config.get("sensitivity", "5.0"))

            while(controlRunning()):
                firing = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000 > 0
                _AGC.setFiring(firing)

                aiming = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000 > 0
                _AGC.setAiming(aiming)

                movementKB = _AGC.config.get("movement-keybind", "VK_XBUTTON1")
                if(movementKB.startswith("ASCII")): movementKeyCode = ord(movementKB.split("_")[-1])
                else: movementKeyCode = getattr(win32con, movementKB, win32con.VK_XBUTTON1)
                moving = win32api.GetAsyncKeyState(movementKeyCode) & 0x8000 > 0
                _AGC.setMoving(moving)

                _AGC.setNading(grenadeMode)

                if(firing):
                    keyboard.send(os.environ["KEY_SHOOTING"], do_press=True, do_release=False)
                    if(GameMonitor.weaponConfig and GameMonitor.weaponConfig.get("tap", False) and not grenadeMode):
                        keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
                    gunMul = float(GameMonitor.weaponConfig.get("multiplier", "1.0"))
                    recoil = GameMonitor.weaponConfig.get("recoil", [[0, 0], [0, 0]])
                    if(aiming):
                        win32api.mouse_event(
                            win32con.MOUSEEVENTF_MOVE,
                            round(recoil[recoilIndex%len(recoil)][0]*recoilMultiplier*gunMul),
                            round(recoil[recoilIndex%len(recoil)][1]*recoilMultiplier*gunMul),
                        )
                    recoilIndex = (recoilIndex+1) % len(recoil)
                else:
                    recoilIndex = 0
                    keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)

                if(aiming): grenadeMode = False

                if(moving): keyboard.send(os.environ["KEY_MOVEMENT"], do_press=True, do_release=True)

                time.sleep(1/float(_AGC.config.get("frequency", "120")))

            else:
                grenadeMode = False
                keyboard.send(os.environ["KEY_MOVEMENT"], do_press=False, do_release=True)
                keyboard.send(os.environ["KEY_SHOOTING"], do_press=False, do_release=True)
