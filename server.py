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

from modules import Client

server = Client.Server.Server()
server.run(host=server.host, port=server.port, threaded=True)

[
    '/Users/leefuuchang/Desktop/ApexGunControl-2.0', 
    '/Library/Frameworks/Python.framework/Versions/3.8/lib/python38.zip', 
    '/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8', 
    '/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/lib-dynload', 
    '/Users/leefuuchang/Desktop/ApexGunControl-2.0/env/lib/python3.8/site-packages', 
    'ApexGunControl-LS/be'
]