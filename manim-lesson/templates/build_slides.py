"""课堂版构建:渲染分步动画 → manim-slides 按章转 reveal.js → 插入交互页 → 输出 output/slides/。

分章设计(2026-10-08):课堂时间有弹性(90 分钟设计,80 分钟可能讲完、也可能讲不完),
课堂版按章节出**独立文件** ch1.html~chN.html + 目录页 index.html——教师讲到哪章开哪个文件,
章界即天然断点,没讲完下次直接开下一章;章内中断可靠 URL hash(#/页码)续讲。
视频版不受影响,仍出单个 mp4。

用法:
  python build_slides.py              # 1080p30
  python build_slides.py --quality l  # 低画质预览
  python build_slides.py --skip-render
  python build_slides.py --only S00Demo
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from _env import MS, FFMPEG, REPO
from build_video import SCENES, TITLE, run
from narration import SCRIPT

ROOT = Path(__file__).resolve().parent
SLIDES_DIR = ROOT / "build" / "slides_slides"
OUT = ROOT / "output" / "slides"
WEB = ROOT / "web"
KATEX_SRC = REPO / "assets" / "lesson" / "libs" / "katex"  # 本地 KaTeX,禁 CDN

# 章节划分:(文件id, 章节标题, [场景类...])。场景须不重不漏覆盖 SCENES 全集且顺序一致(构建时断言)。
# 交互页跟随其 INTERACTIVE 登记的场景落在对应章里。
CHAPTERS = [
    ("ch1", "第一章 · 示例", ["S00Demo"]),
]

# 交互页插在哪个场景之后。例:INTERACTIVE = {"S04Squares": "squares.html"}
INTERACTIVE = {}

# 交互页内按方向键时,iframe 会截获键盘事件 → 交互页用 postMessage 转给这里
BRIDGE = """
<script>
  window.addEventListener('message', function (e) {
    if (!e.data || e.data.type !== 'reveal-nav') return;
    if (e.data.dir === 'next') Reveal.next();
    else if (e.data.dir === 'prev') Reveal.prev();
  });
  // 离开交互页时把焦点还给主页面,方向键继续可用
  Reveal.on('slidechanged', function () { window.focus(); });
</script>
"""

# 目录页:投影可读(深色底、大字),点击进章
INDEX = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{title} · 课堂演示</title>
<style>
  body {{ background:#0b0d10; color:#e8ecf1; font-family:"Microsoft YaHei",sans-serif;
         display:flex; flex-direction:column; align-items:center; justify-content:center;
         min-height:100vh; margin:0; }}
  h1 {{ font-size:2.2em; font-weight:600; }}
  a {{ display:block; width:16em; margin:.5em; padding:.7em 1em; font-size:1.5em;
       color:#e8ecf1; text-decoration:none; border:1px solid #3a4250; border-radius:12px; }}
  a:hover {{ border-color:#7fb069; }}
  a small {{ display:block; font-size:.55em; color:#9aa4b2; margin-top:.3em; }}
</style></head><body>
<h1>{title}</h1>
{links}
</body></html>
"""


def page_counts(classes):
    """每个场景有几页(从 manim-slides 的 json 读),据此找插入位置。"""
    return [len(json.loads((SLIDES_DIR / f"{c}.json").read_text("utf-8"))["slides"]) for c in classes]


# 半自动课件(2026-10-08):每页翻页自动播 TTS + 底部字幕条,方向键翻页、空格暂停/继续旁白。
# 页 → 旁白段映射:step=True 段起新页,后续非 step 段并入同页连播(与 step_notes 同规则)。
SEMIAUTO_CSS = """
<style>
  #subtitle { position:fixed; left:50%; bottom:5vh; transform:translateX(-50%);
    max-width:82vw; padding:.3em .9em; background:rgba(8,10,14,.78); color:#fff;
    font:600 2.6vmin/1.5 "Microsoft YaHei",sans-serif; border-radius:.4em;
    z-index:60; display:none; text-align:center; }
</style>
<div id="subtitle"></div>
"""

SEMIAUTO_JS = """
<script>
var PAGES = __PAGES__;  // 与 section 顺序一一对应;交互页为 null
(function () {
  var sub = document.getElementById('subtitle');
  var audio = new Audio();
  var cur = -1, fileIdx = 0;
  function playFile() {
    var p = PAGES[cur];
    if (!p || fileIdx >= p.files.length) { sub.style.display = 'none'; return; }
    audio.src = p.files[fileIdx][0];
    var pr = audio.play();
    if (pr && pr.catch) pr.catch(function () {});  // 首次交互前的拒绝由 keydown 兜底
  }
  function playPage(i) {
    audio.pause(); sub.style.display = 'none';
    cur = i; fileIdx = 0;
    if (PAGES[i]) playFile();
  }
  audio.addEventListener('ended', function () { fileIdx++; playFile(); });
  audio.addEventListener('timeupdate', function () {
    var p = PAGES[cur]; if (!p) return;
    var t = p.starts[fileIdx] + audio.currentTime, txt = '';
    for (var k = 0; k < p.cues.length; k++) if (p.cues[k][0] <= t) txt = p.cues[k][1];
    if (txt) { sub.textContent = txt; sub.style.display = 'block'; }
  });
  Reveal.on('ready', function (e) { playPage(e.indexh); });
  Reveal.on('slidechanged', function (e) { playPage(e.indexh); });
  // 空格:当前页有旁白时 = 暂停/继续(拦截,不翻页);交互页等无旁白页保持 reveal 默认(翻页)
  document.addEventListener('keydown', function (e) {
    if (e.code === 'Space' && PAGES[Reveal.getIndices().h]) {
      e.preventDefault(); e.stopPropagation();
      if (audio.paused) { audio.play().catch(function () {}); } else { audio.pause(); }
    } else if (audio.paused && audio.src && PAGES[cur]) {
      audio.play().catch(function () {});  // 浏览器自动播放策略:首次任意按键解锁当前页旁白
    }
  }, true);
  window.__semi = audio;  // 调试句柄:控制台可查播放状态
})();
</script>
"""


def page_playlist(classes, durations):
    """每页的播放清单:{files:[[src,dur]], starts:[累计起点], cues:[[全局秒,字幕]]}。"""
    pages = []
    for c in classes:
        groups = []
        for n in SCRIPT[c[:3]]:  # 类名前 3 位 = SCRIPT 键(同 common.py scene_id)
            if n.step or not groups:
                groups.append([n])
            else:
                groups[-1].append(n)
        for g in groups:
            files, starts, cues, t = [], [], [], 0.0
            for n in g:
                assert n.key in durations, f"{n.key} 缺音频,先跑 python tts.py"
                d = durations[n.key]
                files.append([f"audio/{n.key}.mp3", d["duration"]])
                starts.append(t)
                cues += [[t + a, txt] for a, _, txt in d["sentences"]]
                t += d["duration"]
            pages.append({"files": files, "starts": starts, "cues": cues})
    return pages


# 课堂版必须离线可用(教室网络不可控,2026-10-09 实测 jsdelivr 连接重置):
# reveal.js 运行库 vendor 进 web/vendor/revealjs/(来源 npmmirror tarball),convert 产物里的 CDN 前缀统一改写
REVEAL_CDN = "https://cdn.jsdelivr.net/npm/reveal.js@6.0.1/dist"


def build_chapter(cid, ctitle, classes, env, durations):
    """convert 一章 → 断页数 → 插交互页 → 挂半自动播放与翻页桥,返回 (页数, 交互页数)。"""
    out = OUT / f"{cid}.html"
    run([MS, "convert", "--folder", SLIDES_DIR, *classes, out,
         "-ccontrols=true", "-cprogress=true", "-cslide_number=c/t", "-chash=true",
         f"-ctitle={TITLE} · {ctitle}", "-cpreload_iframes=true"], cwd=ROOT, env=env)
    html = out.read_text("utf-8")
    assert REVEAL_CDN in html, f"{cid} 未找到 reveal.js CDN 前缀,模板可能变了,离线改写失效"
    html = html.replace(REVEAL_CDN, "vendor/revealjs")
    counts = page_counts(classes)
    sections = list(re.finditer(r"<section\b.*?</section>", html, flags=re.S))
    assert len(sections) == sum(counts), f"{cid} 页数不一致:HTML {len(sections)},json 合计 {sum(counts)}"
    pages = page_playlist(classes, durations)
    assert len(pages) == sum(counts), f"{cid} 旁白分组 {len(pages)} ≠ 页数 {sum(counts)}(narration 的 step 与渲染分步不一致)"
    inserts = {}
    sec_end = 0   # 原 section 序列的游标(不含插入的交互页)
    page_idx = 0  # 播放清单的游标(含交互页占位)
    for c, n in zip(classes, counts):
        sec_end += n
        page_idx += n
        if c in INTERACTIVE:
            inserts[sections[sec_end - 1].end()] = (
                f'\n        <section data-background-iframe="{INTERACTIVE[c]}" data-background-interactive '
                f'data-background-color="#0b0d10">\n          <aside class="notes">交互页:请学生上台拖动。'
                f'方向键 / 空格仍可翻页。</aside>\n        </section>')
            pages.insert(page_idx, None)  # 交互页无旁白,占位保持与 section 对齐
            page_idx += 1
    for pos in sorted(inserts, reverse=True):
        html = html[:pos] + inserts[pos] + html[pos:]
    payload = json.dumps(pages, ensure_ascii=False)
    assert "</script>" not in payload
    html = html.replace("</body>",
                        SEMIAUTO_CSS + SEMIAUTO_JS.replace("__PAGES__", payload) + BRIDGE + "</body>")
    out.write_text(html, "utf-8")
    return sum(counts), len(inserts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", default="h", choices=["l", "m", "h"])
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    env = {**os.environ, "PYTHONUTF8": "1", "LS_MODE": "slides"}
    env["PATH"] = env["PATH"] + os.pathsep + str(Path(FFMPEG).parent)

    flat = [c for _, _, cs in CHAPTERS for c in cs]
    assert flat == [c for _, c in SCENES], "CHAPTERS 必须不重不漏覆盖 SCENES 且顺序一致"

    if not a.skip_render:
        t0 = time.time()
        for f, c in SCENES:
            if a.only and c not in a.only:
                continue
            # 不能写成 -qh:manim-slides 自己的参数解析会把它拆成 -q -h(help),打印帮助后以 0 退出
            cmd = [MS, "render", "--quality", a.quality,
                   "--media_dir", ROOT / "build" / "media_slides", ROOT / "scenes" / f"{f}.py", c]
            if a.quality == "h":
                cmd[4:4] = ["--fps", "30"]
            run(cmd, cwd=ROOT, env=env)
            # 渲染"成功"却没产出时,convert 会悄悄用上一次的旧 json → 这里必须报错
            js = SLIDES_DIR / f"{c}.json"
            assert js.exists() and js.stat().st_mtime > t0, f"{c} 没有生成新的 {js.name},渲染可能没有真正执行"

    if OUT.exists():
        shutil.rmtree(OUT)  # 若有进程(http.server/打开课件.bat)cwd 在此会报 WinError 32,先关掉
    OUT.mkdir(parents=True)

    # 半自动课件:全部旁白音频 + 句级时间戳
    durations = json.loads((ROOT / "audio" / "durations.json").read_text("utf-8"))
    (OUT / "audio").mkdir()
    for f in (ROOT / "audio").glob("*.mp3"):
        shutil.copy(f, OUT / "audio" / f.name)

    links, total = [], 0
    for cid, ctitle, classes in CHAPTERS:
        n_anim, n_inter = build_chapter(cid, ctitle, classes, env, durations)
        total += n_anim + n_inter
        links.append(f'<a href="{cid}.html">{ctitle}<small>{n_anim + n_inter} 页</small></a>')
    (OUT / "index.html").write_text(
        INDEX.format(title=TITLE, links="\n".join(links)), "utf-8")

    if WEB.exists():
        for f in WEB.iterdir():
            if f.is_dir():  # vendor/ 等目录整树复制
                shutil.copytree(f, OUT / f.name)
            else:
                shutil.copy(f, OUT / f.name)
    assert (OUT / "vendor" / "revealjs" / "reveal.js").exists(), "web/vendor/revealjs 缺失,课堂版离线不可用"
    if KATEX_SRC.exists():
        shutil.copytree(KATEX_SRC, OUT / "katex")  # 交互页引 katex/katex.min.css 相对路径
    # file:// 下部分浏览器限制 iframe/视频 → 附一个本地服务器启动脚本
    (OUT / "打开课件.bat").write_text(
        '@echo off\r\ncd /d "%~dp0"\r\nstart "" http://localhost:8765/index.html\r\n'
        'python -m http.server 8765\r\n', encoding="gbk")
    print(f"完成:{OUT / 'index.html'}  共 {len(CHAPTERS)} 章 {total} 页")


if __name__ == "__main__":
    main()
