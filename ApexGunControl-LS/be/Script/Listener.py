from pynput import mouse, keyboard
from typing import Union



class InputState(dict):
    def __getitem__(self, key: Union[str, mouse.Button, keyboard.Key, keyboard.KeyCode]) -> bool:
        return super().__getitem__(key if(isinstance(key, str))else repr(key))
    
    def __setitem__(self, key: Union[str, mouse.Button, keyboard.Key, keyboard.KeyCode], value: bool) -> None:
        return super().__setitem__(key if(isinstance(key, str))else repr(key), value)



class Mouse:
    Button = mouse.Button

    listener: mouse.Listener = None

    controller: mouse.Controller = mouse.Controller()

    pressed: InputState = InputState({repr(button):False for button in mouse.Button})

    @classmethod
    def Move(cls, dx: int, dy: int):
        cls.controller.move(dx, dy)

    @classmethod
    def OnClick(cls, x: int, y: int, button: mouse.Button, pressed: bool):
        cls.pressed[repr(button)] = pressed

if(Mouse.listener is None):
    Mouse.listener = mouse.Listener(
        on_click=Mouse.OnClick,
        daemon=True,
    )
    Mouse.listener.start()



class Keyboard:
    Key = keyboard.Key

    listener: keyboard.Listener = None

    pressed: InputState = InputState({repr(key):False for key in keyboard.Key})

    @classmethod
    def OnPress(cls, key: keyboard.KeyCode):
        cls.pressed[repr(key)] = True

    @classmethod
    def OnRelease(cls, key: keyboard.KeyCode):
        cls.pressed[repr(key)] = False

if(Keyboard.listener is None):
    Keyboard.listener = keyboard.Listener(
        on_press=Keyboard.OnPress,
        on_release=Keyboard.OnRelease,
        daemon=True,
    )
    Keyboard.listener.start()