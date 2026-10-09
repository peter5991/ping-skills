"""模拟"页陆续到达":把齐备的页资产按节奏发布到 jit 目录,验证播放器的热升级行为。

用法:
  python simulate.py --src <assets_dir> --dst <jit_dir> [--frame-delay 8] [--clip-delay 20] [--page-gap 12]

assets_dir 结构:
  manifest.full.json   {"title":..., "pages":[{"id","title","text","notes","audio":true/false}, ...]}
  pages/<id>/text.html | frame.png | clip.mp4 | audio.mp3

发布节奏(相对该页文字稿到达):text 立即 → frame +frame-delay → clip +clip-delay;页与页错开 page-gap。
"""
import argparse
import json
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def publish(dst, manifest):
    tmp = dst / "manifest.json.tmp"
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")
    tmp.replace(dst / "manifest.json")  # 原子替换,播放器不会读到写一半的 manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--dst", required=True, type=Path)
    ap.add_argument("--frame-delay", type=float, default=8)
    ap.add_argument("--clip-delay", type=float, default=20)
    ap.add_argument("--page-gap", type=float, default=12)
    a = ap.parse_args()

    full = json.loads((a.src / "manifest.full.json").read_text("utf-8"))
    if a.dst.exists():
        shutil.rmtree(a.dst)
    (a.dst / "pages").mkdir(parents=True)
    for f in ("player.html", "serve.py"):
        shutil.copy(HERE / f, a.dst / f)

    # 初始:全部 pending
    manifest = {"title": full["title"],
                "pages": [{**p, "state": "pending"} for p in full["pages"]]}
    publish(a.dst, manifest)

    # 事件表:(时刻, 页下标, 阶段, 源文件)
    events = []
    for i, p in enumerate(full["pages"]):
        t0 = i * a.page_gap
        events.append((t0, i, "text"))
        events.append((t0 + a.frame_delay, i, "frame"))
        events.append((t0 + a.clip_delay, i, "clip"))
    events.sort()

    start = time.time()
    for t, i, stage in events:
        dt = t - (time.time() - start)
        if dt > 0:
            time.sleep(dt)
        p = full["pages"][i]
        src_dir = a.src / "pages" / p["id"]
        dst_dir = a.dst / "pages" / p["id"]
        dst_dir.mkdir(exist_ok=True)
        if stage == "text":
            if (src_dir / "text.html").exists():
                shutil.copy(src_dir / "text.html", dst_dir / "text.html")
            if (src_dir / "audio.mp3").exists():  # 语音与文字稿同批到达(TTS 在渲染前完成)
                shutil.copy(src_dir / "audio.mp3", dst_dir / "audio.mp3")
        elif stage == "frame":
            shutil.copy(src_dir / "frame.png", dst_dir / "frame.png")
        else:
            shutil.copy(src_dir / "clip.mp4", dst_dir / "clip.mp4")
        manifest["pages"][i]["state"] = stage
        publish(a.dst, manifest)
        print(f"[{time.time() - start:5.1f}s] {p['id']} -> {stage}")
    print("全部页发布完成")


if __name__ == "__main__":
    main()
