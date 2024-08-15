import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import requests as rq
import importlib
import traceback
import platform
import logging
import random
import atexit
import types
import json
import sys
import os



"""
Environment Variables
"""
if(not hasattr(os, "default_environ")): setattr(os, "default_environ", os.environ.copy())

os.environ["TIMEZONE"] = "Asia/Taipei"

os.environ["PROJECT_NAME"] = "ApexGunControl"

os.environ["APP_USER_MODEL_ID"] = f"{os.environ['PROJECT_NAME']}.App.User.Model.Id"

os.environ["SERVER_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}"
os.environ["STORAGE_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}/Storage"
os.environ["MODULES_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}/Modules"

os.environ["USER_AGENT"] = random.choice([
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15"
])

if getattr(sys, "frozen", False):
    sys.argv = [arg for arg in sys.argv if not arg.startswith("-")]
    os.environ["EXECUTABLE_ROOT"] = os.path.dirname(sys.executable)
else:
    os.environ["EXECUTABLE_ROOT"] = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))



"""
Logging Configuration
"""
os.environ["SYSTEM_INFO_PATH"] = os.path.join(os.environ["EXECUTABLE_ROOT"], "system.json")
with open(os.environ["SYSTEM_INFO_PATH"], "w", encoding="UTF-8") as f: 
    json.dump(platform.uname()._asdict(), f, indent=4, ensure_ascii=False)

logger = logging.getLogger()

logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s", "%Y-%m-%dT%H:%M:%S")

cout_handler = logging.StreamHandler(sys.stdout)
cout_handler.setLevel(logging.DEBUG)
cout_handler.setFormatter(formatter)
logger.addHandler(cout_handler)

os.environ["LOG_HANDLER_PATH"] = os.path.join(os.environ["EXECUTABLE_ROOT"], "logs.log")
log_handler = logging.FileHandler(os.environ["LOG_HANDLER_PATH"], "w")
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)

def UploadCrashLog(exc_type, exc_value, exc_traceback):
    logging.error(f"Crash Log Uploading:\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}")
    if("--debug" in sys.argv): sys.exit(1)
    default_environ = getattr(os, "default_environ", {})
    try:
        with open(os.environ["LOG_HANDLER_PATH"], "rb") as log_file, \
             open(os.environ["SYSTEM_INFO_PATH"], "rb") as sys_file:
            rq.post(
                f"{os.environ['SERVER_URL']}/CrashReport", 
                data={key:os.environ[key] for key in os.environ if key not in default_environ},
                files={
                    os.path.split(os.environ["LOG_HANDLER_PATH"])[1]: log_file,
                    os.path.split(os.environ["SYSTEM_INFO_PATH"])[1]: sys_file,
                },
            )
    except Exception as e:
        logging.error(f"Log Upload Fail:\n{''.join(traceback.format_exception(e.__class__, e, e.__traceback__))}")
    return sys.exit(1)
sys.excepthook = UploadCrashLog

atexit.register(lambda:logging.info("Program exited"))



"""
Remote Module
"""
def RemoteImport(name):
    if(name in sys.modules): return sys.modules[name]

    root = os.environ["EXECUTABLE_ROOT"]
    if(root not in sys.path): sys.path.append(root)

    if("--debug" in sys.argv):
        path = os.path.join(root, f"{name}.py")
        if(os.path.exists(path)):
            sys.modules[name] = importlib.import_module(name)
            return sys.modules.get(name, None)
        raise ModuleNotFoundError(name)

    module = types.ModuleType(name)
    logging.info(f"Installing Remote Package: {name}")
    try: 
        res = rq.get(f"{os.environ['MODULES_URL']}/{name}.py")
        exec(res.text, module.__dict__)
        sys.modules[name] = module
    except Exception as e: 
        logging.error(f"Falied to Install Remote Package: {name} {e}")
        return UploadCrashLog(e.__class__, e, e.__traceback__)

    if(name in sys.modules): 
        return sys.modules[name]
    raise ModuleNotFoundError(name)
