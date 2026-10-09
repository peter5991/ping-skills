# jit.md — JIT 临场生成(实验路线)

**状态:实验,只在用户明确说「manim」时触发,不主动启用(2026-10-08 决策)。** 是否进入课堂临场路线取决于生成速度实测(决策①:够快则支持"提问后现场生成 3-5 页小课",不够快则只用于备课)。

## 设想

不完全生成 MP4。课堂演示 = 页序列,教师方向键控制;**讲第 N 页时 Agent 后台制作第 N+1 页**,翻页即看动画;每页可带 TTS 语音,翻到自动讲(edge-tts,决策③),讲完教师补充,补充完翻页,循环。

## 分层流水线(消化"生成时间不确定"的核心)

| 层 | 内容 | 时机 |
|---|---|---|
| ① 脚本 | 全部页 narration(讲什么、分几步) | 最先,一次生成 |
| ② 语音 | 全部页 TTS(tts.py edge 后端) | 紧跟①,与文字稿同批发布 |
| ③ 场景代码 | 每页一个场景类,**只用 recipes.py 配方拼装** | 逐页 |
| ④ 渲染 | 每页 clip.mp4 + frame.png | 逐页排队 |

①②完成后(目标 <1 分钟)教师就有完整讲稿+全部配音;每页三级渐进 **text → frame → clip**,播放器按"当前有什么放什么"渲染,资产到达即热替换。教师永远有东西讲,动画是增强不是前提。

> 注意:临场路线的①层 narration ≠ 备课态的 SCRIPT.md。**临场不写 SCRIPT.md、不做脚本评审**(2026-10-08 决策:临场没有时间,①层一次生成即开干);SCRIPT.md 是备课态工作流程第 1 步,只对全量构建生效。

## 协议(player ↔ producer)

```
jit/
  player.html        # 播放器(轮询 manifest,no-store)
  serve.py           # 本地服务器(manifest 禁缓存)
  manifest.json      # {"title":..., "pages":[{"id","title","text","notes","audio":bool,"state"}]}
  pages/<id>/text.html | frame.png | clip.mp4 | audio.mp3
```

- `state`: `pending → text → frame → clip`,只升不降;producer 原子写 manifest(写 .tmp 再 replace)
- `frame.png` 取 clip 的代表帧(ffmpeg 抽 ~80% 处)
- 播放器:1s 轮询;资产优先级 clip>frame>text;换页/升级才重绘,**语音不打断**;键位 →/← 翻页、空格暂停·继续语音、N 备注
- 语音与文字稿同批到达(TTS 前置);页停留期间音频到达自动开播

## 思考模式(2026-10-08 决策,助教/Pi Agent 集成时注意)

- **Pi Agent 默认关闭思考模式;制作动画 Slide 时临时开启**,让模型自行设计动画制作方案与脚本——负责人明确倾向模型自己设计,配方库(references/recipes.md)仅作参考(非数学课程配方覆盖不到)。备课模式/其他 Agent 同理:配方只作参考。
- 开思考后单页耗时约 2~3 分钟,**可接受**(配合 2 页预读缓冲)。
- **实测(2026-10-08,L02 ch2 首次模拟助教生成)**:pi CLI 0.80.6 + DeepSeek(`deepseek-flash`,anthropic-messages 端点,thinking=high,配置同 app models.json 模板),一次会话产出两幕场景(S04 七步链+回环 / S05 四原则围拢)+ narration.py 追加 4 段 + 自检,**共 164s(≈82s/幕,含读文档/写码/自检)**,一次通过零返工(句数断言、py_compile、缩略图过目、Chrome 翻页+hash 续讲全过)。结论:备课态批量生成完全可行;临场 2 页预读节奏可行,是否支持「提问后现场生成」待课堂实测拍板(决策①)。复现方式:`PI_CODING_AGENT_DIR=<隔离models.json目录> pi -p --model custom/<模型> --thinking high --skill .claude/skills/manim-lesson`(models.json 照 electron/agent/config.ts 模板生成)。
- **回退预案**:若实测开思考耗时过长,负责人会关掉思考、改走"只填配方参数"的约束模式(届时 recipes.md 恢复为强制约束)。

## 与既有路线的分工(判据待课堂实测后拍板)

- 备课态全量构建(build_video/build_slides)= 默认;JIT 与全量**同一套场景源码**,只是组装方式不同(每页独立场景类,而非一幕多步)
- 与 pagegen 临场页:Manim JIT 候选判据 = 需要精确动画推导的数学/物理内容;pagegen 仍是秒级、带 mark 锚点的默认临场路线
- 播放器自研薄层(templates/jit/player.html),不用 manim-slides convert(它要求全量场景齐了一次性组装)

## 观察仓(agent 桥,不进默认路径)

- [MCP-Manim-Slides](https://github.com/antoniomachuca/MCP-Manim-Slides)(3★,MIT):MCP Server 让 agent 渲染 manim-slides、预览单页、导出 Reveal HTML——与 JIT 临场路线同向。**仅观察**,星少,用前自验 MCP 稳定性与离线能力;教室离线/分章/TTS 同步仍靠自有 build(2026-10-09 记,详见 upstream-tracking.md)。

## 骨架验证

`templates/jit/simulate.py --src <assets> --dst <jit>` 按节奏发布齐备资产(text 立即 / frame +8s / clip +20s / 页间隔 12s,均可调),配合 `serve.py` 验证播放器热升级行为。实测数据记 log.md 2026-10-08 JIT 条。
