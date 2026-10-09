#!/bin/bash
# 低画质预览渲染:./render_ql.sh s00_demo:S00Demo ...
export PYTHONUTF8=1 PATH="$PATH:$HOME/AppData/Local/Microsoft/WinGet/Links"
cd "$(dirname "$0")"
# 向上查找共享环境
d=$(pwd); while [ "$d" != "/" ] && [ ! -x "$d/tools/manim-env/.venv/Scripts/python.exe" ]; do d=$(dirname "$d"); done
PY="$d/tools/manim-env/.venv/Scripts/python.exe"
[ -x "$PY" ] || { echo "找不到共享环境 tools/manim-env/.venv,先跑 tools/manim-env/setup.sh"; exit 1; }
for a in "$@"; do
  f=${a%%:*}; c=${a##*:}
  out=$("$PY" -m manim render -ql --media_dir build/media scenes/$f.py $c 2>&1)
  if echo "$out" | grep -q "Traceback"; then echo "== $c FAILED"; echo "$out" | grep -A3 -E "^\s*(File|.*Error)" | tail -25; else
    v=build/media/videos/$f/480p15/$c.mp4; ./preview.sh $v build/p_$c.png ${IV:-3}
    echo "== $c OK $(ffprobe -v error -show_entries format=duration -of csv=p=0 $v)s"; fi
done
