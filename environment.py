import requests as rq
import logging
import atexit
import sys
import os



"""
Environment Variables
"""
os.environ["VERSION"] = "4.3.0"

os.environ["PROJECT_NAME"] = "ApexGunControl"

os.environ["SERVER_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}"
os.environ["STORAGE_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}/Storage"

if getattr(sys, "frozen", False):
    os.environ["EXECUTABLE_ROOT"] = os.path.dirname(sys.executable)
else:
    os.environ["EXECUTABLE_ROOT"] = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))



"""
Logging Configuration
"""
logger = logging.getLogger()

logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s", "%Y-%m-%dT%H:%M:%S")

cout_handler = logging.StreamHandler(sys.stdout)
cout_handler.setLevel(logging.DEBUG)
cout_handler.setFormatter(formatter)
logger.addHandler(cout_handler)

file_handler_path = os.path.join(os.environ["EXECUTABLE_ROOT"], "logs.log")
file_handler = logging.FileHandler(file_handler_path, "w")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    try:
        logging.disable(logging.CRITICAL)
        with open(file_handler_path, "rb") as log_file:
            rq.post(f"{os.environ['SERVER_URL']}/CrashReport", files={"Log":(file_handler_path, log_file)})
    except Exception as e:
        logger.error(f"Crash Log Upload Failed {e}")
    finally:
        logging.disable(logging.NOTSET)
sys.excepthook = handle_exception

def handle_exit():
    logger.info("Program exited")
atexit.register(handle_exit)