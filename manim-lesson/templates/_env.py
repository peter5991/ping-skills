"""定位共享 Manim 环境(tools/manim-env/.venv)。

课件项目可放在仓库内任意深度(默认 output/manim-lessons/<主题>/),向上查找仓库根。
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_repo_root(start=ROOT):
    for d in [start, *start.parents]:
        if (d / "tools" / "manim-env" / ".venv" / "Scripts" / "python.exe").exists():
            return d
    raise SystemExit("找不到 tools/manim-env/.venv —— 先运行 tools/manim-env/setup.sh 搭建共享环境")


REPO = find_repo_root()
VENV = REPO / "tools" / "manim-env" / ".venv" / "Scripts"
PY = VENV / "python.exe"          # 共享环境 python
MS = VENV / "manim-slides.exe"    # manim-slides 入口
FFMPEG = shutil.which("ffmpeg") or str(Path.home() / "AppData/Local/Microsoft/WinGet/Links/ffmpeg.exe")
FFPROBE = shutil.which("ffprobe") or str(Path.home() / "AppData/Local/Microsoft/WinGet/Links/ffprobe.exe")
