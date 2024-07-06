from mss import mss
import numpy as np
import cv2
import sys
import os


class Detector:
    mss = mss()
    monitor = [m for m in mss.monitors[1:] if(m["left"]==0 and m["top"]==0)][0]

    defaultB = 1080 // 6

    @staticmethod
    def regionOf(w, h):
        b = h//6
        return (w-b*3, h-b, w, h)

    @staticmethod
    def similarityOf(base, match):
        result = cv2.matchTemplate(base, match, cv2.TM_CCOEFF_NORMED)
        return cv2.minMaxLoc(result)[1]

    @staticmethod
    def capture():
        region = Detector.regionOf(Detector.monitor["width"], Detector.monitor["height"])
        return np.array(Detector.mss.grab(region))

    @staticmethod
    def detect(screenshot, prioritize, confidence):
        img = cv2.resize(screenshot, (Detector.defaultB*3, Detector.defaultB), interpolation=cv2.INTER_NEAREST)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

        silhouettes = os.path.join("ApexGunControl-LS", "apex", "silhouettes")

        if(prioritize):
            sil = cv2.imread(os.path.join(silhouettes, f"{prioritize}.jpg"), cv2.IMREAD_UNCHANGED)
            if(Detector.similarityOf(img, sil) > confidence):
                return prioritize

        for file in os.listdir(silhouettes):
            if(not file.endswith(".jpg")): continue
            sil = cv2.imread(os.path.join(silhouettes, file), cv2.IMREAD_UNCHANGED)
            if(Detector.similarityOf(img, sil) > confidence): return os.path.splitext(file)[0]

        return None



if __name__ == "__main__":
    if(len(sys.argv) > 1):
        screenshot = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED)
        w = screenshot.shape[1]
        h = screenshot.shape[0]
        r = Detector.regionOf(w, h)
        screenshot = screenshot[r[1]:r[3], r[0]:r[2]]
    else:
        screenshot = Detector.capture()
    print(Detector.detect(screenshot, "", 0.8))