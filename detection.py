import cv2
import sys
import os

def DetectOn(screenShot, prevWeapon, confidence):
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

print(DetectOn(cv2.imread(sys.argv[1]), "R-301", 0.8))