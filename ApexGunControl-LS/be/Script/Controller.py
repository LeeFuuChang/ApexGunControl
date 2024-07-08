import threading
import time
import os



class Controller:
    thread = None

    @classmethod
    def update(cls):
        while(not time.sleep(.5)):
            while(os.environ["USER"]):
                pass



if(Controller.thread is None):
    Controller.thread = threading.Thread(target=Controller.update, daemon=True)
    Controller.thread.start()


