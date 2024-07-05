from PIL import ImageGrab
import numpy as np
import time
import cv2

time.sleep(5)

screenshot = ImageGrab.grab()

w = screenshot.width
h = screenshot.height

base = h//6

img = screenshot.crop((w-base*3, h-base, w, h))

img = np.array(img.convert("RGB"))

img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

cv2.imwrite("screenshot.png", img)