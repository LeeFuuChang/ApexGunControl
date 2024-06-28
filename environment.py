
import sys, os

os.environ["PROJECT_NAME"] = "ApexGunControl"

os.environ["SERVER_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}"
os.environ["STORAGE_URL"] = f"https://www.leefuuchang.in/projects/{os.environ['PROJECT_NAME']}/Storage"

if getattr(sys, "frozen", False):
    os.environ["EXECUTABLE_ROOT"] = os.path.dirname(sys.executable)
else:
    os.environ["EXECUTABLE_ROOT"] = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))