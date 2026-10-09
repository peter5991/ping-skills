#!/bin/bash
# 用法: ./preview.sh <视频> <输出png> [每隔几秒一帧]  -> 生成缩略图拼图,便于检查画面
export PATH="$PATH:$HOME/AppData/Local/Microsoft/WinGet/Links"
iv=${3:-3}
ffmpeg -v error -y -i "$1" -vf "fps=1/$iv,scale=480:-1,tile=4x4" -frames:v 1 "$2"
