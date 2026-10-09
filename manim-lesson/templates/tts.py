"""配音生成,TTS 后端可插拔。

产出契约(无论哪个后端):
- audio/<key>.mp3
- audio/durations.json  {key: {path, duration, hash, sentences: [[start, end, text], ...]}}
  sentences 的时间是该段音频内的相对秒,text 是对应的字幕句子。
按 (朗读文本, 后端参数) 的哈希缓存:改一句只重新生成一句。

后端:
- edge(默认):edge-tts,SentenceBoundary 事件给精确句时间;断句对不上时降级按字数比例分配。
- external:用 audio_src/<key>.mp3 现成音频(教师自录/其他 TTS),只测时长,句子按字数比例分配。
接新后端(如本地 MOSS-TTS):写一个产出 (duration, bounds) 的函数,注册进 BACKENDS。

用法: python tts.py [--backend edge|external]
"""
import argparse
import asyncio
import hashlib
import json
import re
import shutil
from pathlib import Path

from mutagen.mp3 import MP3

from narration import ALL, speak_of

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
SRC = ROOT / "audio_src"
DUR_FILE = AUDIO / "durations.json"

# edge 后端参数
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "-10%"  # 教学节奏更从容;总时长不够再加停顿,别只压语速


def split_sentences(t):
    return [s for s in re.findall(r"[^。!?]+[。!?]?", t) if s.strip()]


def h(n, tag):
    return hashlib.md5(f"{speak_of(n)}|{tag}".encode()).hexdigest()[:12]


def allocate(n, dur, bounds):
    """句边界 → sentences;句数对不上时按字数比例分配(降级但可用)。"""
    subs = split_sentences(n.text)
    if len(bounds) == len(subs):
        return [[a, b, t] for (a, b), t in zip(bounds, subs)]
    print(f"  ⚠ {n.key}: 句边界 {len(bounds)} 句,字幕 {len(subs)} 句,改用字数比例")
    start, end = (bounds[0][0], bounds[-1][1]) if bounds else (0.0, dur)
    total = sum(len(s) for s in subs)
    sentences, t = [], start
    for s in subs:
        d = (end - start) * len(s) / total
        sentences.append([t, t + d, s])
        t += d
    return sentences


# ---------- 后端:edge ----------

async def synth_edge(n, sem, results):
    import edge_tts
    async with sem:
        path = AUDIO / f"{n.key}.mp3"
        bounds = []
        for attempt in range(3):
            try:
                bounds.clear()
                comm = edge_tts.Communicate(speak_of(n), VOICE, rate=RATE, boundary="SentenceBoundary")
                with open(path, "wb") as f:
                    async for ch in comm.stream():
                        if ch["type"] == "audio":
                            f.write(ch["data"])
                        elif ch["type"] == "SentenceBoundary":
                            bounds.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7))
                break
            except Exception as e:  # 网络抖动重试
                print(f"  重试 {n.key}: {e!r}")
                await asyncio.sleep(2)
        else:
            raise RuntimeError(f"edge-tts 失败: {n.key}")
        dur = MP3(path).info.length
        print(f"  {n.key}: {dur:.2f}s")
        results[n.key] = {"path": str(path), "duration": dur, "hash": h(n, f"edge|{VOICE}|{RATE}"),
                          "sentences": allocate(n, dur, bounds)}


async def run_edge(todo, old):
    results = {}
    sem = asyncio.Semaphore(4)
    await asyncio.gather(*(synth_edge(n, sem, results) for n in todo))
    return {k: results.get(k) or old[k] for k in ALL}


# ---------- 后端:external ----------

def run_external(todo, old):
    results = {}
    for n in todo:
        src = SRC / f"{n.key}.mp3"
        assert src.exists(), f"external 后端缺少 {src}(把现成音频放进 audio_src/)"
        path = AUDIO / f"{n.key}.mp3"
        shutil.copy(src, path)
        dur = MP3(path).info.length
        print(f"  {n.key}: {dur:.2f}s (external)")
        results[n.key] = {"path": str(path), "duration": dur, "hash": h(n, f"external|{src.stat().st_mtime}"),
                          "sentences": allocate(n, dur, [])}
    return {k: results.get(k) or old[k] for k in ALL}


BACKENDS = {"edge": ("edge", run_edge), "external": ("ext", run_external)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="edge", choices=list(BACKENDS))
    a = ap.parse_args()
    tag, runner = BACKENDS[a.backend]
    AUDIO.mkdir(exist_ok=True)
    old = json.loads(DUR_FILE.read_text("utf-8")) if DUR_FILE.exists() else {}
    for n in ALL.values():
        assert len(split_sentences(n.text)) == len(split_sentences(speak_of(n))), f"{n.key}: 字幕与朗读句数不同"
    param = {"edge": f"edge|{VOICE}|{RATE}", "ext": None}[tag]
    def cur_hash(n):
        return h(n, param) if param else None  # external 的 hash 依赖源文件,无法预知 → 恒重新处理
    todo = [n for n in ALL.values()
            if a.backend == "external" or not (n.key in old and old[n.key]["hash"] == cur_hash(n) and Path(old[n.key]["path"]).exists())]
    print(f"需要生成 {len(todo)} / {len(ALL)} 段 (backend={a.backend})")
    if asyncio.iscoroutinefunction(runner):
        out = asyncio.run(runner(todo, old))
    else:
        out = runner(todo, old)
    DUR_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
    print(f"总时长 {sum(v['duration'] for v in out.values()):.1f}s")


if __name__ == "__main__":
    main()
