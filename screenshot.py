from mss import mss
import numpy as np
import screeninfo
import cv2

def get_primary_monitor() -> screeninfo.Monitor:
    """Returns the primary monitor by :class:`Monitor`."""
    return [m for m in screeninfo.get_monitors() if m.is_primary][0]

monitor = get_primary_monitor()

w = monitor.width
h = monitor.height

base = h//6

rect = (w-base*3, h-base, w, h)

with mss() as sct:
    img = np.array(sct.grab(rect))

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

    cv2.imwrite("screenshot.png", img)