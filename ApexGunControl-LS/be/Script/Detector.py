from mss import mss
import json
import cv2
import sys
import os



def PreloadRegion(cls):
    cls.load()
    return cls



@PreloadRegion
class Detector:

    monitor = [m for m in mss().monitors[1:] if(m["left"]==0 and m["top"]==0)][0]

    region = (lambda w, h: (w-(h//6)*3, h-(h//6), w, h))(monitor["width"], monitor["height"])

    configPath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("cfg", "settings.json"))

    silhouettesPath = None

    @staticmethod
    def similarityOf(base, match):
        result = cv2.matchTemplate(base, match, cv2.TM_CCOEFF_NORMED)
        return cv2.minMaxLoc(result)[1]

    @classmethod
    def load(cls):
        with open(cls.configPath, "r") as f:
            config = json.load(f)
            l = int(float(config.get("region-l", cls.region[0])))
            t = int(float(config.get("region-t", cls.region[1])))
            r = int(float(config.get("region-r", cls.region[2])))
            b = int(float(config.get("region-b", cls.region[3])))
            cls.region = (
                l if(l >= 0)else cls.region[0],
                t if(t >= 0)else cls.region[1],
                r if(r >= 0)else cls.region[2],
                b if(b >= 0)else cls.region[3],
            )
        for detector in cls.__subclasses__():
            detector.region = cls.region

    @classmethod
    def save(cls):
        with open(cls.configPath, "a+") as f:
            f.seek(0)
            config = json.load(f)
            config.update({
                "region-l": f"{cls.region[0]}",
                "region-t": f"{cls.region[1]}",
                "region-r": f"{cls.region[2]}",
                "region-b": f"{cls.region[3]}",
            })
            f.truncate(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
        for detector in cls.__subclasses__():
            detector.region = cls.region

    @classmethod
    def detect(cls, screenshot):
        if(not cls.silhouettesPath): raise NotImplementedError()

        scale = 1080 / cls.monitor["height"]

        size = (int(screenshot.shape[1]*scale), int(screenshot.shape[0]*scale))

        img = cv2.resize(screenshot, size, interpolation=cv2.INTER_NEAREST)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)[1]

        result = [ None, 0 ]

        for file in os.listdir(cls.silhouettesPath):
            if(not file.endswith(".jpg")): continue
            sil = cv2.imread(os.path.join(cls.silhouettesPath, file), cv2.IMREAD_UNCHANGED)
            sim = cls.similarityOf(img, sil)
            if(sim > result[1]): result = [ os.path.splitext(file)[0], sim ]

        return result



class InGameDetector(Detector):
    silhouettesPath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("apex", "silhouettes", "ingame"))



class WeaponDetector(Detector):
    silhouettesPath = sys.modules["StorageManager"].LocalStorage.path(os.path.join("apex", "silhouettes", "weapons"))
