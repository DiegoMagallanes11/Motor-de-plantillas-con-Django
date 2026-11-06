"""Run the local lab server; also supports the desktop's bundled Python."""
from pathlib import Path
import runpy
import sys

from PIL import Image  # Load the matching native Pillow before path extension.

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
sys.path.append(str(root / ".venv" / "Lib" / "site-packages"))
sys.argv = ["manage.py", "runserver", "127.0.0.1:8008", "--noreload"]
runpy.run_path(str(root / "manage.py"), run_name="__main__")
