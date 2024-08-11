import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import environment
if(len(sys.argv) < 3): raise ValueError(f"too few arguments: `python build.cli.py {{storage path}} {{compile dist}}`")
environment.RemoteImport("StorageCompiler").main(*sys.argv[1:])
environment.RemoteImport("StorageStructure").main(*sys.argv[1:])
os.remove(os.environ["SYSTEM_INFO_PATH"])
os.remove(os.environ["LOG_HANDLER_PATH"])