from pynput import mouse, keyboard
from typing import Union



class InputState(dict):
    def __getitem__(self, key: Union[str, mouse.Button, keyboard.Key, keyboard.KeyCode]) -> bool:
        return super().__getitem__(key if(isinstance(key, str))else repr(key))
    
    def __setitem__(self, key: Union[str, mouse.Button, keyboard.Key, keyboard.KeyCode], value: bool) -> None:
        return super().__setitem__(key if(isinstance(key, str))else repr(key), value)



class Mouse:
    listener: mouse.Listener = None

    controller: mouse.Controller = mouse.Controller()

    pressed: InputState = InputState({repr(button):False for button in mouse.Button})

    @staticmethod
    def Move(dx: int, dy: int):
        Mouse.controller.move(dx, dy)

    @staticmethod
    def OnClick(x: int, y: int, button: mouse.Button, pressed: bool):
        Mouse.pressed[repr(button)] = pressed

if(Mouse.listener is None):
    Mouse.listener = mouse.Listener(
        on_click=Mouse.OnClick,
        daemon=True,
    )
    Mouse.listener.start()



class Keyboard:
    listener: keyboard.Listener = None

    controller: keyboard.Controller = keyboard.Controller()

    pressed: InputState = InputState({repr(key):False for key in keyboard.Key})

    @staticmethod
    def OnPress(key: keyboard.KeyCode):
        Keyboard.pressed[repr(key)] = True

    @staticmethod
    def OnRelease(key: keyboard.KeyCode):
        Keyboard.pressed[repr(key)] = False

if(Keyboard.listener is None):
    Keyboard.listener = keyboard.Listener(
        on_press=Keyboard.OnPress,
        on_release=Keyboard.OnRelease,
        daemon=True,
    )
    Keyboard.listener.start()