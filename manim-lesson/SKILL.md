---
name: manim-lesson
description: "Manim 动画课件制作工作流:一套场景源码产出双产物——配音讲解成片 mp4(自动播放) + 课堂分步 reveal.js 课件(教师控制节奏,可嵌 SVG 交互教具页)。当用户说'做动画课件''Manim 课件''讲解视频''动画演示课',或要把数学/物理等需要精确动画推导的内容做成视频+演示课件时使用。与单 HTML 课件体系(lesson-prep/pagegen)互补,不替代:本 skill 适合备课态的重型动画推导课,临场快速生成仍走 pagegen。"
---

# manim-lesson — Manim 动画课件双产物工作流

把一堂课做成**一套源码、两种产物**:

- **视频版**:`output/<主题>.mp4`——逐幕动画 + edge-tts 配音 + 烧录字幕,自动播放,适合预习/复习/宣讲
- **课堂版**:`output/slides/`——reveal.js 分步课件,**半自动**(2026-10-08):翻页自动播 TTS 旁白 + 底部字幕条逐句同步(句级时间戳来自 durations.json),方向键翻页(回翻重播)、**空格暂停/继续旁白**(教师插话用)、S 开演讲者备注;**按章节拆成独立文件** ch1.html~chN.html + 目录页 index.html(课堂时间有弹性:讲到哪章开哪个,章界即断点,没讲完下次直接开下一章;章内中断靠 URL hash 续讲);可在指定幕后嵌入**纯 SVG 交互教具页**(学生上台拖动,交互页无旁白、方向键/空格仍可翻页),附 `打开课件.bat` 本地服务器

蒸馏自已验证的最小二乘法课件项目(2026-10-08,38 页课堂版 + 10 分钟成片,音画同步数据验证通过)。

## 不可破的红线

1. **环境唯一**:只用共享环境 `tools/manim-env/.venv`(搭建见该目录 README),禁在课件项目里自建 venv。所有命令 `PYTHONUTF8=1`,cwd = 课件项目根目录(manim-slides 相对路径按 cwd 解析)。
2. **产物仅本地,完成品交付进课程文件夹**(2026-10-08 二轮决策):课件项目源码落 `output/manim-lessons/<主题>/`,**不入库、不接 links.md**;但**每章验收通过后,产物复制进对应课程文件夹** `assets/lesson/<课程>/<课>/动画课件/`(`slides/` 整个目录 + mp4 + srt)——assets/lesson 课程内容本就仅本地不入库,交付与仓库边界不冲突(被否决项:产物只留 output/,因为教师找不到;进 links.md/被软件引用,因为动画课件是备课态独立产物,不接临场管线)。教师用 `动画课件/slides/打开课件.bat` 本地打开。
3. **数字纪律**:画面上出现的每个数字都由 `data.py` 算出,`python data.py` 跑断言与独立方法(如 `np.polyfit`)对拍;旁白里的数字必须来自同一数据源。禁手写数字。
4. **旁白双轨**:`narration.py` 每段同时维护字幕文本 `text` 与朗读文本 `speak`(数字/公式改中文读法),两者按 。!? 切出的句数必须相等(tts.py 有断言)。
5. **投影可读与美学纪律**(2026-10-09 扩写,原仅"黑底大字"):近黑深底 `BG=#0B0D10`(禁纯黑——投影上发灰发死;与课堂版网页底色一致,双产物视觉连续);配色只用 `common.py` 设计令牌——**一课一主色**,每课在 SCRIPT.md §2.5 从候选(青/薄荷/金/珊瑚)选一个 `ACCENT` 填回 `common.py`,场景内禁发明颜色、禁 manim 出厂色(尤其 `#FFFF00` 纯黄);字级阶梯 标题 48 / 正文 32 / 注脚 22(`SIZE_TITLE/BODY/NOTE`,投影可读下限,不再小);动效 ease-out、入场一次性、方向有语义(下入=新内容,侧入=推进);画面下方 `SUB_SAFE_Y` 以下留给烧录字幕不放内容;中文用 `Text(font="Microsoft YaHei")`,MathTex 只排公式。
6. **fail-loud**:每幕渲染后断言产物 json 的 mtime 晚于构建起点(模板已内置)——manim-slides 的 `-qh` 会被拆成 `-q -h` 静默失败,这是血泪教训,详见 references/pitfalls.md #7。
7. **课堂版整体离线,禁任何 CDN**(2026-10-09 扩大,原仅交互页):教室网络不可控(实测 jsdelivr 连接重置整页白屏)。reveal.js 运行库已 vendor 进 `templates/web/vendor/revealjs/`(6.0.1,源自 npmmirror tarball,随模板复制、入库跟踪,与 katex 同规),`build_slides.py` 把 convert 产物的 CDN 前缀改写为本地路径并断言改写生效;KaTeX 用本地 `assets/lesson/libs/katex`,图片素材零外链。

## 技术权威源 = references/ + templates/

| 文件 | 内容 | 何时读 |
|---|---|---|
| `references/environment.md` | 依赖清单、搭建、环境坑 | 环境出问题/换机器时 |
| `references/architecture.md` | 双模式单源码架构、narration/data/tts 契约、构建管线 | **动笔前必读** |
| `references/recipes.md` | M1~M6 配方库(**参考用,非强制**;默认模型自行设计动画方案,代码 = templates/recipes.py) | 写场景时参照 |
| `references/jit.md` | JIT 临场生成实验路线(分层流水线/播放器协议/触发词) | 做 JIT 相关前 |
| `references/interactive.md` | 交互教具页范式(拖动手柄/目标函数侧栏/最佳记录/揭晓按钮/吸附)与已踩坑 | 做交互页前 |
| `references/pitfalls.md` | 14 个已踩坑的根因与对策 + 音画同步/黑帧验证技术 | 出 bug 先查这里 |
| `references/upstream-tracking.md` | 上游/对照仓跟踪表(上次核对日+跟踪结论+已否决方向) | 例行收集 diff 时 |
| `templates/` | 可直接复制的项目脚手架(common/narration/data/tts/recipes/build_*/web/scenes 示例 + jit/ 播放器) | 开新项目时 |

## JIT 临场生成(实验路线,「manim」触发词)

除备课态全量构建外,另有一条**实验中的 JIT 临场路线**:页陆续生成、播放器热升级、每页带 TTS 自动讲。**只在用户明确说「manim」时使用,不主动触发**(2026-10-08 决策);协议与分层流水线见 `references/jit.md`。**临场路线不写 SCRIPT.md、不做脚本评审**(临场没有时间,①层 narration 一次生成即开干)——SCRIPT.md 第一步只对备课态生效(2026-10-08 决策)。助教(Pi Agent)内使用时注意:**制作动画 Slide 临时打开思考模式**,让模型自行设计方案,配方库仅作参考(jit.md「思考模式」条)。

## 工作流程

1. **教学脚本与内容设计(备课态第一步,先于一切代码)**:在 `output/manim-lessons/<主题>/SCRIPT.md` 写教学脚本(骨架照 `templates/SCRIPT.md`,完成实例见 l02-modeling)——课堂时间轴→**章节(章=独立 slides 文件,对应教学环节,3~5 章为宜)**→幕映射、叙事弧、逐幕旁白草案(text/speak/step)、数据需求清单(每个上屏数字先实测预演)、交互页计划、验收口径。**教师过目通过后才动工**;此后 narration.py/data.py 只是 SCRIPT.md 的代码化,内容改动先改 SCRIPT.md。JIT 临场路线无此步(见 jit.md)。
2. **开项目**:复制模板 `cp -r .claude/skills/manim-lesson/templates/* output/manim-lessons/<主题>/`(不含 templates/README.md;SCRIPT.md 已在第 1 步写好,别被模板覆盖)。
3. **内容落定**:把 SCRIPT.md 的幕清单与旁白翻进 `narration.py`(text/speak/step 三要素,step=课堂版分步点)。
4. **数据**:`data.py` 按 SCRIPT.md 数据需求清单写全片数据与派生数值,跑通断言。
5. **配音**:`python tts.py`(默认 edge-tts;换后端见 architecture.md TTS 契约)生成 `audio/` + `durations.json`。
6. **逐幕场景**:`scenes/sNN_*.py`,低画质快速迭代 `./render_ql.sh s00_demo:S00Demo` 出缩略图拼图逐帧过目,修完再下一幕。
7. **交互教具页**(可选):`web/` 下纯 SVG+vanilla 页,在 `build_slides.py` 的 `INTERACTIVE` 登记插入位置。
8. **构建双产物**:`python build_video.py --quality l` / `python build_slides.py --quality l` 低画质验证(逐章页数断言、末帧黑帧检测、Chrome 实测交互页)→ 通过后 `--quality h` 出 HQ。课堂版分章 = build_slides.py 的 `CHAPTERS` 配置(场景不重不漏覆盖全集,有断言)。
9. **验收**:视频版做音画同步数据验证(silencedetect 对字幕起点,分段查累积漂移,方法见 pitfalls.md #13);课堂版 Chrome 打开逐页翻一遍 + 交互页拖一遍,console 零报错;外加 SCRIPT.md 第 5 节的本课内容红线复查。截图/录屏给负责人过目。
10. **交付**:验收通过后把产物复制进对应课程文件夹 `assets/lesson/<课程>/<课>/动画课件/`(`slides/` 整目录 + mp4 + srt;后续章节增量覆盖同名文件即可),并在交付目录起一次 http.server 冒烟测(翻几页 + console 零报错, favicon 404 不算)确认拷贝完整。
