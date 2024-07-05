from mss import mss
import numpy as np
import screeninfo
import cv2
import os


def detect(rect, prevWeapon, confidence):
    with mss() as screen: 
        screenShot = np.array(screen.grab(rect))

        img = cv2.cvtColor(screenShot, cv2.COLOR_BGR2GRAY)

        img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

        silhouettes = os.path.join("ApexGunControl-LS", "apex", "silhouette")

        def confidenceOf(weaponName):
            nonlocal img, silhouettes
            sil = cv2.imread(os.path.join(silhouettes, f"{weaponName}.jpg"), cv2.IMREAD_UNCHANGED)
            result = cv2.matchTemplate(img, sil, cv2.TM_CCOEFF_NORMED)
            return cv2.minMaxLoc(result)[1]

        if(prevWeapon and confidenceOf(prevWeapon) > confidence): return prevWeapon

        for file in os.listdir(silhouettes):
            if(not file.endswith(".jpg")): continue
            weaponName = os.path.splitext(file)[0]
            if(confidenceOf(weaponName) > confidence): return weaponName

    return None


monitor = [m for m in screeninfo.get_monitors() if m.is_primary][0]

w = monitor.width
h = monitor.height

base = h//6

rect = (w-base*3, h-base, w, h)

print(detect(rect, "", 0.8))