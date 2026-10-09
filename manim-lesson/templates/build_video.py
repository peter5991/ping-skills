"""视频版构建:渲染全部场景 → 生成字幕 → 拼接 → 烧录字幕。

用法:
  python build_video.py               # 高画质 1080p60(-qh)
  python build_video.py --quality l   # 低画质预览
  python build_video.py --skip-render # 只重新拼接/做字幕
  python build_video.py --only S00Demo
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from _env import PY, FFMPEG, FFPROBE

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
OUT = ROOT / "output"
TITLE = "演示课件"  # 改成课题名,决定输出文件名

# (文件, 类) 按播放顺序
SCENES = [
    ("s00_demo", "S00Demo"),
]
QDIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}
MAX_CHARS = 18  # 每条字幕最多字数


def run(cmd, **kw):
    print("$", " ".join(map(str, cmd))[:200])
    subprocess.run(list(map(str, cmd)), check=True, **kw)


def duration(p):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def split_long(text, start, end):
    """把一句话按逗号等切成不超过 MAX_CHARS 的小段,时间按字数比例分配。"""
    text = text.strip()
    if len(text) <= MAX_CHARS:
        return [(start, end, text)]
    parts = re.findall(r"[^，、；：,]+[，、；：,]?", text)
    chunks, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > MAX_CHARS:
            chunks.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        chunks.append(cur)
    # 仍超长的硬切
    final = []
    for c in chunks:
        while len(c) > MAX_CHARS + 4:
            final.append(c[:MAX_CHARS])
            c = c[MAX_CHARS:]
        final.append(c)
    total = sum(len(c) for c in final)
    out, t = [], start
    for c in final:
        d = (end - start) * len(c) / total
        out.append((t, t + d, c))
        t += d
    return out


def srt_time(t):
    ms = int(round(t * 1000))
    h_, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h_:02}:{m:02}:{s:02},{ms:03}"


def build_srt(offsets):
    durs = json.loads((ROOT / "audio" / "durations.json").read_text("utf-8"))
    items = []
    for (_, cls), off in zip(SCENES, offsets):
        cues = json.loads((BUILD / "cues" / f"{cls}.json").read_text("utf-8"))
        for key, start in cues:
            for a, b, text in durs[key]["sentences"]:
                for s, e, c in split_long(text, a, b):
                    c = c.rstrip("，、；：,。")
                    items.append((off + start + s, off + start + e, c))
    lines = []
    for i, (s, e, c) in enumerate(items, 1):
        lines += [str(i), f"{srt_time(s)} --> {srt_time(e)}", c, ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", default="h", choices=QDIR)
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--only", nargs="*", help="只渲染这些类")
    a = ap.parse_args()
    env = {**os.environ, "PYTHONUTF8": "1", "LS_MODE": "video"}
    env["PATH"] = env["PATH"] + os.pathsep + str(Path(FFMPEG).parent)
    if not a.skip_render:
        for f, c in SCENES:
            if a.only and c not in a.only:
                continue
            run([PY, "-m", "manim", "render", f"-q{a.quality}", "--media_dir", BUILD / "media", ROOT / "scenes" / f"{f}.py", c],
                cwd=ROOT, env=env)
    vids = [BUILD / "media" / "videos" / f / QDIR[a.quality] / f"{c}.mp4" for f, c in SCENES]
    offsets, t = [], 0.0
    for v in vids:
        offsets.append(t)
        t += duration(v)
    print(f"总时长 {t:.1f}s = {t / 60:.1f} 分钟")
    OUT.mkdir(exist_ok=True)
    work = BUILD / "final"
    work.mkdir(parents=True, exist_ok=True)
    (work / "list.txt").write_text("".join(f"file '{v.as_posix()}'\n" for v in vids), "utf-8")
    full = work / "full.mp4"
    # 统一重新编码拼接(各场景都带音轨,参数一致,但重编码最稳妥)
    run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", work / "list.txt",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", full])
    srt = build_srt(offsets)
    (work / "full.srt").write_text(srt, "utf-8")
    import shutil
    shutil.copy(work / "full.srt", OUT / f"{TITLE}.srt")
    style = ("FontName=Microsoft YaHei,FontSize=17,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
             "BackColour=&H80000000,BorderStyle=1,Outline=1.2,Shadow=0.6,MarginV=8")
    # subtitles 滤镜里 Windows 路径的冒号难转义 → 在 work 目录中用相对文件名
    run([FFMPEG, "-v", "error", "-y", "-i", "full.mp4", "-vf", f"subtitles=full.srt:force_style='{style}'",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy",
         "subbed.mp4"], cwd=work)
    name = f"{TITLE}.mp4" if a.quality == "h" else f"{TITLE}_{QDIR[a.quality]}.mp4"
    shutil.move(work / "subbed.mp4", OUT / name)
    print("完成:", OUT / name)


if __name__ == "__main__":
    main()
