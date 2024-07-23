import requests as rq
import importlib
import logging
import types
import sys
import os

def Import(name, retries=3):
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
    for t in range(retries):
        logging.info(f"Package Installing {name} (tries:{t+1})")
        try: 
            res = rq.get(f"{os.environ['STORAGE_URL']}/{name}.py")
            exec(res.text, module.__dict__)
            sys.modules[name] = module
        except Exception as e: 
            logging.error(f"Package Install Error {name} {e}")
        break

    if(name in sys.modules): 
        return sys.modules[name]
    raise ModuleNotFoundError(name)

