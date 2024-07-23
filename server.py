import environment
import sys
import os

import PackageManager
PackageManager.Import("StorageManager")

LocalStorage = sys.modules["StorageManager"].LocalStorage

LocalStorage.setup(os.environ["STORAGE_URL"], os.environ["EXECUTABLE_ROOT"])

sys.path.append(LocalStorage.path("be"))

from Server.Flask import WebServer

server = WebServer()
server.run(host=server.host, port=server.port, threaded=True)