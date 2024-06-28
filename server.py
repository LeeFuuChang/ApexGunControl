import environment

import sys, os
sys.path.append("ApexGunControl-LS/be")

from PackageManager import getPackage
LocalStorage = getattr(getPackage("StorageManager", os.environ["STORAGE_URL"]), "LocalStorage")(os.environ["STORAGE_URL"])

from modules import Client


server = Client.Server.Server()
server.run(threaded=True)