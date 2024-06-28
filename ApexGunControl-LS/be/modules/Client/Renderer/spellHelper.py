from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QGraphicsOpacityEffect, QMenu, QAction
from PyQt5 import QtCore, QtGui

import screeninfo, difflib, logging, time, os
logger = logging.getLogger()

from PackageManager import getPackage
StorageManager = getPackage("StorageManager", os.environ["STORAGE_URL"])
LocalStorage = getattr(StorageManager, "LocalStorage").getInstance()

from ...thread import TaskThread

from .utility import setLeftClickable, setRightClickable


def sendInProgressChat(messages):
    pass


class SpellHelperPlayer(QWidget):
    def __init__(self, parent, index):
        super(self.__class__, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        self.format = None

        self._parent = parent
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)

        self.data = {
            "index": index,
            "thread": None,
            "summonerName": "",
            "championName": "",
            "rawChampionName": "",
            "championLabel": QLabel(),
            "championPixmap": QtGui.QPixmap(),
            "championImageURL": "",
            "spell1": {
                "hotkey": "D",
                "counter": {
                    "label": QLabel(),
                    "opacity": QGraphicsOpacityEffect(),
                },
                "notify": {
                    "label": QLabel(),
                    "opacity": QGraphicsOpacityEffect(),
                },
                "label": QLabel(),
                "pixmap": QtGui.QPixmap(),
                "thread": None,
                "tw": "",
                "en": "",
                "displayName": "",
                "rawDisplayName": "",
                "imageURL": "",
                "castTime": 0,
                "cooldown": 0,
                "fullCooldown": 0,
            },
            "spell2": {
                "hotkey": "F",
                "counter": {
                    "label": QLabel(),
                    "opacity": QGraphicsOpacityEffect(),
                },
                "notify": {
                    "label": QLabel(),
                    "opacity": QGraphicsOpacityEffect(),
                },
                "label": QLabel(),
                "pixmap": QtGui.QPixmap(),
                "thread": None,
                "tw": "",
                "en": "",
                "displayName": "",
                "rawDisplayName": "",
                "imageURL": "",
                "castTime": 0,
                "cooldown": 0,
                "fullCooldown": 0,
            },
            "styles": {
                "notify-color": {
                    "c": "#000000",
                    "a": 8
                },
                "counter-color": {
                    "c": "#ffffff",
                    "a": 10
                }
            }
        }

        self.updateSpellDisplay("spell1")
        self.updateSpellDisplay("spell2")

        self.connectSpellCallbacks("spell1")
        self.connectSpellCallbacks("spell2")

        setLeftClickable(self.data["championLabel"]).connect(self.startBroadcastSpellCooldown)

        self.data["championLabel"].setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.data["championLabel"].customContextMenuRequested.connect(self.emptySpaceMenu)


    def emptySpaceMenu(self):
        clickPos = QtGui.QCursor.pos()
        contents = [
            ["重新載入玩家", lambda:(self.reloadPixmap(), self.updateLayout(), self.updateSize()), True],
            ["重新載入圖片", lambda:(self.reloadPixmap(), self.updateSize()), True],
            ["重新載入版面", self._parent.updateLayout, True],
            ["重新計算冷卻", self.updateLayout, True],
            ["按住滾輪可以移動哦！", lambda:None, True],
        ]
        menu = QMenu()
        for text, func, state in contents:
            action = QAction(text)
            action.setEnabled(state)
            action.triggered.connect(func)
            menu.addAction(action)
        menu.exec_(clickPos)


    def reloadPixmap(self):
        with self._parent.server.test_client() as client:
            champRequest = client.get(self.data["championImageURL"])
            self.data["championPixmap"].loadFromData(champRequest.data)
            spell1Request = client.get(self.data["spell1"]["imageURL"])
            self.data["spell1"]["pixmap"].loadFromData(spell1Request.data)
            spell2Request = client.get(self.data["spell2"]["imageURL"])
            self.data["spell2"]["pixmap"].loadFromData(spell2Request.data)

    def updateSize(self, size=None):
        if(size): self.size = size
        self.layout.setContentsMargins(self.size//16, self.size//16, self.size//16, self.size//16)

        self.data["championLabel"].setFixedSize(2*self.size, 2*self.size)
        self.data["championLabel"].setPixmap(self.data["championPixmap"].scaled(2*self.size, 2*self.size))

        def resizeSpell(key):
            self.data[key]["counter"]["label"].setFixedSize(self.size, self.size)
            self.data[key]["notify"]["label"].setFixedSize(self.size, self.size)
            self.data[key]["label"].setFixedSize(self.size, self.size)
            self.data[key]["label"].setPixmap(self.data[key]["pixmap"].scaled(self.size, self.size))
        resizeSpell("spell1")
        resizeSpell("spell2")

        self.setFixedSize(self.layout.sizeHint())

    def updateLayout(self, layoutFormat=None):
        if(not layoutFormat): layoutFormat = self._parent.format
        if(layoutFormat == "format-u"): pos = [(0, 0), (0, 1), (1, 0)]
        if(layoutFormat == "format-d"): pos = [(2, 0), (2, 1), (0, 0)]
        if(layoutFormat == "format-l"): pos = [(0, 0), (1, 0), (0, 1)]
        if(layoutFormat == "format-r"): pos = [(0, 3), (1, 3), (0, 0)]
        self.format = layoutFormat
        def replaceSpell(key, p):
            self.layout.removeWidget(self.data[key]["counter"]["label"])
            self.layout.removeWidget(self.data[key]["notify"]["label"])
            self.layout.removeWidget(self.data[key]["label"])
            self.layout.addWidget(self.data[key]["counter"]["label"], *p, 1, 1, QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.data[key]["notify"]["label"], *p, 1, 1, QtCore.Qt.AlignCenter)
            self.layout.addWidget(self.data[key]["label"], *p, 1, 1, QtCore.Qt.AlignCenter)
        replaceSpell("spell1", pos[0])
        replaceSpell("spell2", pos[1])
        self.layout.removeWidget(self.data["championLabel"])
        self.layout.addWidget(self.data["championLabel"], *pos[2], 2, 2, QtCore.Qt.AlignCenter)


    def calculateCooldown(self, baseCooldown, abilityHaste):
        # https://leagueoflegends.fandom.com/wiki/Haste
        return int( baseCooldown * ( 100 / (100+abilityHaste) ) )

    def calculateSpellCastTime(self, key):
        self.endBroadcastSpellCooldown()
        def getAbilityHaste(description):
            begString = "<attention> "
            endString = "</attention> Ability Haste"
            if(endString not in description): return 0
            endIndex = description.find(endString)
            description = description[:endIndex]
            begIndex = description.rfind(begString)+len(begString)
            description = description[begIndex:]
            if(not description.isnumeric()): return 0
            else: return int(description)
        with self._parent.server.test_client() as client:
            name = self.data["summonerName"]
            playerItems = []
            try: playerItemsRequest = client.get(f"/riot/ingame/playeritems", query_string={"summonerName":name}).get_json(force=True)
            except: playerItemsRequest = {"success": False}
            if(not playerItemsRequest["success"]): return False
            else: playerItems = playerItemsRequest["response"]
            hasteList = [getAbilityHaste(self._parent.itemsData.get(i["itemID"], "")) for i in playerItems]
            abilityHaste = sum(hasteList)
            self.data[key]["cooldown"] = self.calculateCooldown(self.data[key]["fullCooldown"], abilityHaste)
            logger.info(f"[SpellHelper] recorded {key} cast time (abilityHaste: {abilityHaste:>2}) ( {self.data['championName']} )")
            return True

    def endSetSpellCastTime(self, key):
        if(self.data[key]["thread"] is not None):
            self.data[key]["thread"].event.set()
        self.data[key]["thread"] = None

    def setSpellCastTime(self, key):
        self.data[key]["castTime"] = time.time()
        self.data[key]["thread"] = TaskThread(
            target=self.calculateSpellCastTime,
            interval=0,
            delay=0,
            tries=50,
            fargs=(key, ),
            onFinished=lambda:self.endSetSpellCastTime(key)
        ).start()

    def resetSpellCastTime(self, key):
        self.endBroadcastSpellCooldown()
        self.endSetSpellCastTime(key)
        self.data[key]["castTime"] = 0
        self.data[key]["cooldown"] = 0

    def connectSpellCallbacks(self, key):
        spl_L = self.data[key]["label"]
        cnt_L = self.data[key]["counter"]["label"]
        not_L = self.data[key]["notify"]["label"]
        setLeftClickable(spl_L).connect(lambda:self.setSpellCastTime(key))
        setLeftClickable(cnt_L).connect(lambda:self.setSpellCastTime(key))
        setLeftClickable(not_L).connect(lambda:self.setSpellCastTime(key))
        setRightClickable(spl_L).connect(lambda:self.resetSpellCastTime(key))
        setRightClickable(cnt_L).connect(lambda:self.resetSpellCastTime(key))
        setRightClickable(not_L).connect(lambda:self.resetSpellCastTime(key))

    def updateSpellDisplay(self, key):
        cover = self.data[key]["castTime"]>0

        spl_L = self.data[key]["label"]
        cnt_O = self.data[key]["counter"]["opacity"]
        cnt_L = self.data[key]["counter"]["label"]
        not_O = self.data[key]["notify"]["opacity"]
        not_L = self.data[key]["notify"]["label"]

        cnt_O.setOpacity((self.data["styles"]["counter-color"]["a"]/10) * cover)
        cnt_L.setStyleSheet(f"color:{self.data['styles']['counter-color']['c']}")
        cnt_L.setGraphicsEffect(cnt_O)
        cnt_L.setAlignment(QtCore.Qt.AlignCenter)

        not_O.setOpacity((self.data["styles"]["notify-color"]["a"]/10) * cover)
        not_L.setStyleSheet(f"background:{self.data['styles']['notify-color']['c']}")
        not_L.setGraphicsEffect(not_O)

        not_L.stackUnder(cnt_L)
        spl_L.stackUnder(not_L)

    def updateSpell(self, key, base):
        castTime = self.data[key]["castTime"]
        if(castTime): 
            cooldown = self.data[key]["cooldown"]
            leftTime = cooldown-int(base-castTime)
            self.data[key]["castTime"] *= (leftTime > 0)
            if(self.data[key]["castTime"]): 
                self.data[key]["counter"]["label"].setText(f"{leftTime}")
        self.updateSpellDisplay(key)


    def broadcastSpellCooldown(self):
        nowTime = time.time()
        with self._parent.server.test_client() as client:
            # try: spellOverallOptions = client.get("/config/settings/game/auto-lane/message").get_json(force=True)
            # except: spellOverallOptions = {}
            # if(not spellOverallOptions): return False

            try: spellOverallNickname = client.get("/config/settings/spell/overall/nickname").get_json(force=True)
            except: spellOverallNickname = {}
            if(not spellOverallNickname): return False

            try: spellSendOptions = client.get("/config/settings/spell/send/options").get_json(force=True)
            except: spellSendOptions = {}
            if(not spellSendOptions): return False

            try: spellSendFormat = client.get("/config/settings/spell/send/format").get_json(force=True)
            except: spellSendFormat = {}
            if(not spellSendFormat): return False

            try: spellSendNickname = client.get("/config/settings/spell/send/nickname").get_json(force=True)
            except: spellSendNickname = {}
            if(not spellSendNickname): return False

        if(spellSendOptions["champion-name"]): playerNick = self.data["championName"]
        else: playerNick = spellOverallNickname[f"player{self.data['index']+1}"]

        def getSpellString(key):
            if(not spellSendOptions["only-incooldown"] or self.data[key]["castTime"]):
                if(not spellSendOptions["only-flash"] or "Flash" in self.data[key]["rawDisplayName"]):
                    spellNick = self.data[key]["hotkey"]
                    if(spellSendNickname["tw"]):
                        spellNick = self.data[key]["tw"]
                    elif(spellSendNickname["en"]):
                        spellNick = self.data[key]["en"]
                    elif(spellSendNickname["key"]):
                        spellNick = self.data[key]["hotkey"]

                    timeString = "ready"
                    upLeftTime = max(self.data[key]["cooldown"]-int(nowTime-self.data[key]["castTime"]), 0)
                    upGameTime = self.data[key]["castTime"]-self._parent.gameStartTime+self.data[key]["cooldown"]
                    if(not upLeftTime): 
                        timeString = "ready"
                    elif(spellSendFormat["cooldown-s"]):
                        timeString = f"{upLeftTime}s"
                    elif(spellSendFormat["cooldown-m"]):
                        if(not int(upLeftTime/60)): timeString = f"{int(upLeftTime%60)}s"
                        else: timeString = f"{int(upLeftTime/60)}m{int(upLeftTime%60)}s"
                    elif(spellSendFormat["game-time"]):
                        timeString = f"{int(upGameTime/60):0>2}{int(upGameTime%60):0>2}"

                    return f"{spellNick} {timeString}"
            return ""

        spell1str = getSpellString("spell1")
        spell2str = getSpellString("spell2")

        res =  " | ".join(filter(lambda x:x, [playerNick, spell1str, spell2str]))*bool(spell1str or spell2str)

        return sendInProgressChat([res, ])

    def endBroadcastSpellCooldown(self):
        if(self.data["thread"] is not None):
            self.data["thread"].event.set()
        self.data["thread"] = None

    def startBroadcastSpellCooldown(self):
        self.endBroadcastSpellCooldown()
        self.data["thread"] = TaskThread(
            target=self.broadcastSpellCooldown,
            interval=0,
            delay=0,
            tries=50,
            fargs=(),
            onFinished=self.endBroadcastSpellCooldown
        ).start()


    def update(self):
        nowTime = time.time()
        self.updateSpell("spell1", nowTime)
        self.updateSpell("spell2", nowTime)



class SpellHelperUI(QWidget):
    server = None
    setupCompleted = False

    baseSize = size = 24

    supportedModes = ["CLASSIC", "ARAM"]

    spellsData = {
        "SummonerBarrier": {
            "cooldown": 180,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summonerbarrier.png",
            "tw": "光盾",
            "en": "Barrier",
        },
        "SummonerBoost": {
            "cooldown": 210,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_boost.png",
            "tw": "淨化",
            "en": "Cleanse",
        },
        "SummonerDot": {
            "cooldown": 180,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summonerignite.png",
            "tw": "點燃",
            "en": "Ignite",
        },
        "SummonerExhaust": {
            "cooldown": 210,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_exhaust.png",
            "tw": "虛弱",
            "en": "Exhaust",
        },
        "SummonerFlash": {
            "cooldown": 300,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_flash.png",
            "tw": "閃現",
            "en": "Flash",
        },
        "SummonerHaste": {
            "cooldown": 210,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_haste.png",
            "tw": "鬼步",
            "en": "Ghost",
        },
        "SummonerHeal": {
            "cooldown": 240,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_heal.png",
            "tw": "治癒",
            "en": "Heal",
        },
        "SummonerMana": {
            "cooldown": 240,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summonermana.png",
            "tw": "清晰",
            "en": "Mana",
        },
        "SummonerSmite": {
            "cooldown": 15,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_smite.png",
            "tw": "重擊",
            "en": "Smite",
        },
        "SummonerSnowURFSnowball_Mark": {
            "cooldown": 80,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_mark.png",
            "tw": "雪球",
            "en": "Snowball",
        },
        "SummonerSnowball": {
            "cooldown": 80,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_mark.png",
            "tw": "雪球",
            "en": "Snowball",
        },
        "SummonerTeleport": {
            "cooldown": 360,
            "icon": "/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/data/spells/icons2d/summoner_teleport.png",
            "tw": "傳送",
            "en": "Teleport",
        },
    }


    def __init__(self, server, localTeam, gameStats):
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(True)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(self.layout.sizeHint())

        self.format = None

        self.server = server

        self.localTeam = localTeam
        self.gameStats = gameStats
        if(self.gameStats):
            self.gameStartTime = time.time()-self.gameStats["gameTime"]
        else: self.gameStartTime = 0
        self.players = {}


    def __new__(cls, server, localTeam, gameStats):
        if hasattr(cls, "_instance"): return cls._instance
        cls._instance = QWidget.__new__(cls)
        self = cls._instance
        super(self.__class__, self).__init__()
        self.setWindowTitle(os.environ["PROJECT_NAME"])
        self.setWindowIcon(QtGui.QIcon(LocalStorage.path(os.path.join("logo", "Filled.png"))))
        self.setToolTip("按住滑鼠滾輪可以移動")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setupThread = TaskThread(
            target=self.setup,
            interval=0,
            delay=0,
            tries=-1,
            fargs=(),
            onFinished=self.endSetup
        ).start()
        return cls._instance


    def getSpellKey(self, rawDisplayName):
        best = 0
        matched = [*self.spellsData.keys()][0]
        for key in self.spellsData.keys():
            result = difflib.SequenceMatcher(None, key, rawDisplayName)
            if(result.ratio() <= best): continue
            best = result.ratio()
            matched = key
        return matched


    def addPlayer(self, playerData, index):
        helper = SpellHelperPlayer(self, index)

        helper.data["summonerName"] = playerData["summonerName"]
        helper.data["championName"] = playerData["championName"]
        helper.data["rawChampionName"] = playerData["rawChampionName"]
        helper.data["championImageURL"] = f"/cdragon/cdn/champion/{playerData['rawChampionName'].split('_')[3]}/square"

        spell1key = self.getSpellKey("".join(playerData["summonerSpells"]["summonerSpellOne"]["rawDisplayName"].split("_")[2:-1]))
        helper.data["spell1"]["tw"] = self.spellsData[spell1key]["tw"]
        helper.data["spell1"]["en"] = self.spellsData[spell1key]["en"]
        helper.data["spell1"]["imageURL"] = self.spellsData[spell1key]["icon"]
        helper.data["spell1"]["fullCooldown"] = self.spellsData[spell1key]["cooldown"]
        helper.data["spell1"]["displayName"] = playerData["summonerSpells"]["summonerSpellOne"]["displayName"]
        helper.data["spell1"]["rawDisplayName"] = playerData["summonerSpells"]["summonerSpellOne"]["rawDisplayName"]

        spell2key = self.getSpellKey("".join(playerData["summonerSpells"]["summonerSpellTwo"]["rawDisplayName"].split("_")[2:-1]))
        helper.data["spell2"]["tw"] = self.spellsData[spell2key]["tw"]
        helper.data["spell2"]["en"] = self.spellsData[spell2key]["en"]
        helper.data["spell2"]["imageURL"] = self.spellsData[spell2key]["icon"]
        helper.data["spell2"]["fullCooldown"] = self.spellsData[spell2key]["cooldown"]
        helper.data["spell2"]["displayName"] = playerData["summonerSpells"]["summonerSpellTwo"]["displayName"]
        helper.data["spell2"]["rawDisplayName"] = playerData["summonerSpells"]["summonerSpellTwo"]["rawDisplayName"]

        helper.reloadPixmap()

        self.players[playerData["summonerName"]] = helper

        self.updateLayout()


    def endSetup(self):
        self.setupCompleted = True
        if(self.setupThread is not None):
            self.setupThread.event.set()
        self.setupThread = None

    def setup(self):
        if(not self.server): return False
        with self.server.test_client() as client:
            itemsData = None
            try: itemsData = client.get(f"/cdragon/raw/plugins/rcp-be-lol-game-data/global/default/v1/items.json").get_json(force=True)
            except: itemsData = None
            if(itemsData is None): return False
            self.itemsData = {i["id"]:i["description"] for i in itemsData}
        return True


    def reloadStyle(self):
        with self.server.test_client() as client:
            try: overallOptions = client.get(f"/config/appearance/spell/overall/options").get_json(force=True)
            except: overallOptions = {}
            try: overallNotify = client.get(f"/config/appearance/spell/overall/notify-color").get_json(force=True)
            except: overallNotify = {}
            try: overallCounter = client.get(f"/config/appearance/spell/overall/counter-color").get_json(force=True)
            except: overallCounter = {}
        for helper in self.players.values():
            helper.data["styles"]["notify-color"] = overallNotify
            helper.data["styles"]["counter-color"] = overallCounter
        self.format = sorted(["format-u","format-d","format-l","format-r"], key=lambda k:overallOptions.get(k,0))[-1]
        self.size = (self.baseSize * (overallOptions.get("size", 10)/10))


    def updateLayout(self):
        self.reloadStyle()
        if(any([(not helper.format or helper.format != self.format) for helper in self.players.values()])):
            for i in reversed(range(self.layout.count())):
                self.layout.itemAt(i).widget().setParent(None)
        for helper in self.players.values():
            helper.updateLayout(self.format)
            self.layout.removeWidget(helper)
            if(self.format in ["format-u","format-d"]):
                self.layout.addWidget(helper, 0, helper.data["index"], QtCore.Qt.AlignCenter)
            if(self.format in ["format-l","format-r"]):
                self.layout.addWidget(helper, helper.data["index"], 0, QtCore.Qt.AlignCenter)
            helper.updateSize(self.size)
        self.setFixedSize(self.layout.sizeHint())

    def update(self):
        if(not self.setupCompleted): return logger.error("[SpellHelper] Setup Incomplete")
        with self.server.test_client() as client:
            playerList = []
            try: playerListRequest = client.get("/riot/ingame/playerlist").get_json(force=True)
            except: playerListRequest = {"success": False}
            if(playerListRequest["success"]): playerList = playerListRequest["response"]
            playerListNames = {player["summonerName"] for player in playerList}
            for name, helper in self.players.items():
                if(name in playerListNames): continue
                self.layout.removeWidget(helper)
            for idx, player in enumerate(playerList):
                if(player["team"] == self.localTeam): continue
                if(player["summonerName"] in self.players):
                    if(self.players[player["summonerName"]].data["index"] == idx): continue
                    self.players[player["summonerName"]].data["index"] = idx
                else: self.addPlayer(player, idx)
        for helper in self.players.values(): helper.update()
        self.updateLayout()


    def mousePressEvent(self, e):
        if(e.buttons() == QtCore.Qt.MiddleButton):
            self.dragStartPosition = e.globalPos()
        else: self.dragStartPosition = None
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.dragStartPosition = None
        super().mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        if(self.dragStartPosition):
            delta = e.globalPos() - self.dragStartPosition
            self.dragStartPosition = e.globalPos()
            monitors = screeninfo.get_monitors()
            primary = sorted(monitors, key=lambda m:m.is_primary, reverse=True)[0]
            self.move(
                max(0, min(self.x()+delta.x(), primary.width-self.width())),
                max(0, min(self.y()+delta.y(), primary.height-self.height()))
            )
        super().mouseMoveEvent(e)
