import environment
import sys
import os
sys.path.append("ApexGunControl-LS/be")

from PackageManager import getPackage
LocalStorage = getattr(getPackage("StorageManager", os.environ["STORAGE_URL"]), "LocalStorage")
LocalStorage.setup(
    remoteURL = os.environ["STORAGE_URL"],
    directory = os.environ["EXECUTABLE_ROOT"],
)

from Server import WebServer

server = WebServer()
server.run(host=server.host, port=server.port, threaded=True)