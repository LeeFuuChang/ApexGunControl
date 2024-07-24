import environment
environment.RemoteImport("StorageManager")

import sys
import os

LocalStorage = sys.modules["StorageManager"].LocalStorage

LocalStorage.setup(os.environ["STORAGE_URL"], os.environ["EXECUTABLE_ROOT"])

sys.path.append(LocalStorage.path("be"))

from Server.Flask import WebServer

server = WebServer()
server.run(host=server.host, port=server.port, threaded=True)