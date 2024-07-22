import requests as rq
import traceback
import platform
import logging
import atexit
import json
import sys
import os



"""
Environment Variables
"""
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
system_info_path = os.path.join(os.environ["EXECUTABLE_ROOT"], "system.json")
with open(system_info_path, "w") as f: 
    json.dump(platform.uname()._asdict(), f, indent=4, ensure_ascii=False)

logger = logging.getLogger()

logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s", "%Y-%m-%dT%H:%M:%S")

cout_handler = logging.StreamHandler(sys.stdout)
cout_handler.setLevel(logging.DEBUG)
cout_handler.setFormatter(formatter)
logger.addHandler(cout_handler)

log_handler_path = os.path.join(os.environ["EXECUTABLE_ROOT"], "logs.log")
log_handler = logging.FileHandler(log_handler_path, "w")
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.getLogger().error(f"Crash Log Uploading:\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}")
    try:
        with open(log_handler_path, "rb") as log_file, \
             open(system_info_path, "rb") as sys_file:
            rq.post(
                f"{os.environ['SERVER_URL']}/CrashReport", 
                data={
                    "username": os.environ.get("USERNAME" , ""),
                    "password": os.environ.get("PASSWORD" , ""),
                    "expireAt": os.environ.get("EXPIRE_AT", ""),
                },
                files={
                    os.path.split(log_handler_path)[1]: log_file,
                    os.path.split(system_info_path)[1]: sys_file,
                },
            )
    except Exception as e:
        logging.getLogger().error(f"Log Upload Fail:\n{''.join(traceback.format_exception(e.__class__, e, e.__traceback__))}")
    sys.exit(1)
sys.excepthook = handle_exception

def handle_exit():
    logger.info("Program exited")
atexit.register(handle_exit)