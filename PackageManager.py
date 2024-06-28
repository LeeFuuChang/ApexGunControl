import requests as rq
import importlib
import time
import sys
import os



def getPackage(name, storageUrl, retries=3):
    if(name in sys.modules): return sys.modules[name]

    root = os.environ["EXECUTABLE_ROOT"]
    if(root not in sys.path): sys.path.append(root)

    if("--debug" in sys.argv):
        path = os.path.join(root, f"{name}.py")
        if(os.path.exists(path)):
            return importlib.import_module(name)
        raise ModuleNotFoundError(name)

    path = os.path.join(root, f"{name}.pyd")
    for file in os.listdir(root):
        fname, fext = os.path.splitext(file)
        if(fname != name or fext.endswith("py")): continue
        try: os.remove(os.path.join(root, file))
        except Exception as e: continue
    for t in range(retries):
        print(f"Package Installing {name} (tries:{t+1})")
        try: 
            res = rq.get(f"{storageUrl}/{name}.pyd")
            with open(path, "wb") as f: f.write(res.content)
        except Exception as e: continue
        break
    if(os.path.exists(path)): sys.modules[name] = importlib.import_module(name)
    return sys.modules.get(name, None)



def downloadFileByStep(tempPath, realPath, fileStream, chunkSize=4096):
    start_time = time.time()
    total_size = int(fileStream.headers.get("Content-Length", 0))
    ready_size = 0
    yield False, ready_size, total_size, start_time
    with open(tempPath, "wb") as f:
        for data in fileStream.iter_content(chunk_size=chunkSize):
            f.write(data)
            ready_size += len(data)
            yield False, ready_size, total_size, start_time
    if(os.path.exists(realPath)): os.remove(realPath)
    os.rename(tempPath, realPath)
    yield True, ready_size, total_size, start_time