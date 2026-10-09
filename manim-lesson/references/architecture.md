# architecture.md — 双模式单源码架构

**动笔前必读。** 一套场景代码产出两种产物,靠 `LS_MODE=video|slides` 环境变量切换,分步结构只在旁白数据里维护一处。

## 项目结构(模板实例化后)

```
output/manim-lessons/<主题>/
  SCRIPT.md        # 教学脚本与内容设计(备课态第一步产出,先于一切代码;骨架=templates/SCRIPT.md)
  _env.py          # 向上查找 tools/manim-env/.venv,导出 PY/MS/FFMPEG 路径
  common.py        # Lesson/Lesson3D 基类 + voice() + 配色 + T()/fmt()
  narration.py     # 全部旁白(唯一维护处)
  data.py          # 全部数据与派生数值(唯一维护处,直接运行=断言)
  tts.py           # 配音生成,后端可插拔
  build_video.py   # 视频版总装:逐幕渲染 → 字幕 → 拼接 → 烧录
  build_slides.py  # 课堂版总装:manim-slides convert → 插交互页 → 半自动注入(页↔旁白映射+TTS 播放+字幕条) → 翻页桥
  render_ql.sh     # 低画质预览 + 缩略图拼图(迭代主力)
  preview.sh       # 视频 → 4x4 缩略图拼图
  scenes/sNN_*.py  # 每幕一个文件一个场景类
  web/             # 交互教具页(shared.js/shared.css + 每教具一页)
  audio/           # tts.py 产出(mp3 + durations.json)
  build/           # 中间产物(cues/media/final)
  output/          # 最终产物(<主题>.mp4 + .srt + slides/)
```

## 核心机制:`voice()` 上下文管理器

```python
with self.voice("s4_square") as d:   # d = 该段语音时长
    self.play(..., run_time=d * 0.6) # 动画按 d 分配时长
```

- **video 模式**:`add_sound` 配音 + 记录 cue(起点时间,供字幕偏移)→ 块结束后动画短于语音就补 `wait` + 句间停顿 `PAUSE`。
- **slides 模式**:不放声音。分步点 `next_slide(notes=...)` 放在**一段旁白播完之后、下一段是 step 时**——这样两段之间的过渡动画(淡出/移位)属于下一页,每页停在内容完整的画面上。动画时长 = 语音时长 × 0.45(钳制 1.2–4 s),课堂节奏由教师控制。
- `pause(t)` 只在 video 模式等待(教师提问后的留白);`fade_all()` 只在 video 模式清屏(slides 版淡出会造出黑屏页);`skip_reversing = True`(课堂版不生成倒放片段,渲染量减半)。
- `step_break(notes)` 在 slides 模式加不对应旁白的额外分步点。
- 一幕拆多个场景类时(如 3D 碗 + 2D 推导),子类指定 `first_key` 接續旁白,`scene_id` 取类名前三位。

## narration.py 契约

```python
N = namedtuple("N", "key text speak step", defaults=(None, False))
SCRIPT = {"S00": [N("s0_title", "字幕文本", "朗读文本(可省)", step=True), ...], ...}
```

- `text` 上屏字幕;`speak` 给 TTS(数字/公式改中文读法:"y = 68" → "y等于68"),省略则同 text。**两者按 。!? 切出的句数必须相等**,tts.py 开头断言。
- `step=True` = 课堂版这里开新的一步;同一步的所有旁白由 `step_notes()` 合并成该页演讲者备注。
- key 全局唯一(文件里有断言),命名 `s<幕>_<内容>`。

## data.py 契约

- 全片数据 + **所有画面上出现的派生数值**都从这里算;场景与 web 页不手算。
- `python data.py` 直接运行 = 断言全套(与 `np.polyfit` 等独立方法对拍)。
- 旁白里的数字改之前先改 data.py 并重跑断言。

## TTS 契约(后端可插拔)

无论哪个后端,产出契约相同:`audio/<key>.mp3` + `audio/durations.json`:

```json
{"<key>": {"path": "...", "duration": 12.3, "hash": "...",
           "sentences": [[start, end, "字幕句子"], ...]}}
```

- `sentences` 时间是**该段音频内**的相对秒;字幕全局时间 = 幕偏移 + cue 起点 + 句子偏移(build_video.py 算)。
- 后端按 `(朗读文本, 音色/参数)` 哈希缓存,改一句只重新合成一句。
- 已实现后端:`edge`(edge-tts,`SentenceBoundary` 事件给精确句时间;断句对不上时自动降级为按字数比例分配并打印 ⚠)、`external`(用 `audio_src/<key>.mp3` 现成音频——教师自录或别的 TTS——只测时长,句子按字数比例分配)。
- 接新后端(如本地 MOSS-TTS):实现"文本→mp3+句时间",在 `tts.py` 的 `BACKENDS` 注册即可;给不出句时间就按比例分配,字幕精度会降但可用。

## 构建管线

**build_video.py**(`LS_MODE=video`):逐幕 `manim render` → ffprobe 取各幕时长得全局偏移 → 各幕 `build/cues/<Scene>.json` + durations.json 生成 srt(每条 ≤18 字,超长按标点切、时间按字数比例分)→ ffmpeg concat 重编码(libx264 crf18/aac)→ `subtitles` 滤镜烧字幕(Microsoft YaHei,在 srt 所在目录用相对路径)。

**build_slides.py**(`LS_MODE=slides`):逐幕 `manim-slides render --quality X`(**禁 `-qh` 合并写法**)→ 每幕断言产物 json mtime 晚于构建起点 → **按 `CHAPTERS` 配置逐章 `manim-slides convert`**(controls/progress/页码/hash/preload_iframes)出 `ch1.html~chN.html`,另生成目录页 `index.html` → 逐章按各幕 json 页数定位,在 `INTERACTIVE` 登记的幕后插入 `data-background-iframe` 交互页(交互页跟随场景落章)→ **逐章注入半自动播放**(2026-10-08,`page_playlist()`:step=True 段起新页、非 step 段并入同页连播,与 step_notes 同规则;复制 audio/*.mp3 进产物,注入 PAGES 播放清单 + 字幕条 + 播放器 JS——翻页自动播/回翻重播/空格暂停继续/浏览器自动播放策略由首次按键兜底;交互页占位 null 无旁白)→ 逐章注入 postMessage 翻页桥 → 复制 web/* 与本地 katex → 生成 `打开课件.bat`(http.server 8765,开的是目录页)。断言:`CHAPTERS` 场景不重不漏 == SCENES 且顺序一致;每章 HTML section 数 == 该章各幕 json 页数合计 == 旁白分组数(不一致说明 narration 的 step 与渲染分步脱节)。

**分章设计(2026-10-08 决策)**:课堂版按章节出独立文件,视频版仍单个 mp4。动机 = 课堂时间有弹性(90 分钟设计,80 分钟可能讲完、也可能讲不完):章界即断点,教师讲到哪章开哪个文件,没讲完下次直接开下一章;章内中断靠 `-chash=true` 的 URL `#/页码` 续讲。章节与教学环节一一对应(3~5 章为宜),每章首幕第一页带章节标题帧(换文件后学生知道进入哪一章)。
