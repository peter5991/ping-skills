# upstream-tracking.md — 上游仓库跟踪表

**用途**:例行收集任务(开源搜集)的 diff 基线——记录 manim-lesson 管线上游与对照仓的「上次核对日」与跟踪结论,避免每次重新评估。核对时更新「上次核对」列,结论有变才改正文。

> 来源:2026-10-09 开源收集日报告·下午第二轮(D 线 Manim/教学动画扫描)。

## 跟踪表

| 仓库 | License | 与本 skill 的关系 | 结论 | 上次核对 |
|---|---|---|---|---|
| [ManimCommunity/manim](https://github.com/ManimCommunity/manim)(ManimCE) | MIT | 上游运行时,`tools/manim-env` 基于此线 | 例行跟踪 release/changelog,版本漂移再动环境 | 2026-10-09 |
| [jeertmans/manim-slides](https://github.com/jeertmans/manim-slides) | MIT | 课堂版上游(Slide/convert→Reveal) | 跟踪 changelog;vendor reveal **6.0.1** 与上游 convert 默认版本择机对齐——**仅当教室验收出兼容问题才动**(报告原话),平时不追 | 2026-10-09 |
| [ManimCommunity/manim-voiceover](https://github.com/ManimCommunity/manim-voiceover) | MIT | 官方旁白插件(对照) | **不替换**自建 edge-tts 双轨(text/speak + durations.json),除非有明确音色/同步收益;可作「换 TTS 后端」参考 | 2026-10-09 |
| [HarleyCoops/Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim) | MIT | AI→Manim 讲解动画(灵感) | 对照 SCRIPT.md 概念→脚本→幕分解思路;**禁替代 data.py 数字纪律与双产物验收**;生成公式/数字必须人工校 | 2026-10-09 |
| [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) | MIT | 同类 agent skill 形态 | 仅提示词结构样本(星高码旧,2026-01 停推);**勿混用两套环境** | 2026-10-09 |
| [antoniomachuca/MCP-Manim-Slides](https://github.com/antoniomachuca/MCP-Manim-Slides) | MIT | MCP 驱动 manim-slides(低星) | **观察仓**:挂 jit.md,不进生产默认路径;用前自验 MCP 稳定性与离线能力 | 2026-10-09 |
| [ManimCommunity/awesome-manim](https://github.com/ManimCommunity/awesome-manim) | 无 SPDX | 创作者/内容库 | 找范例灵感 | 2026-10-09 |
| [qnguyen3/STEMViz](https://github.com/qnguyen3/STEMViz) | NOASSERTION | LLM→带旁白 STEM 动画(对照) | 思路对照;许可证不清,慎商用 | 2026-10-09 |
| [jeertmans/manim-slides-starter](https://github.com/jeertmans/manim-slides-starter) | MIT | GitHub Pages 部署模板 | 对照「在线挂课件」;教室默认仍本地 bat + 离线 vendor | 2026-10-09 |

## 已否决/勿回头(连同理由,防重复尝试)

- **跟上游 convert 的 CDN Reveal 模板**——否决:教室网络不可控(2026-10-09 jsdelivr 连接重置白屏实测),坚持 skill 离线 vendor(红线 7)。manim-slides `--offline` 同样否决:只是构建时下载,CDN 断了照样失败。
- **用 manim-voiceover 替换 edge-tts 管线**——否决(暂):自建 text/speak 双轨 + durations.json 已支撑句级字幕同步与半自动课件,无收益证据不动。
- **用 manim-slides convert 替代自研 JIT 播放器**——否决:convert 要求全量场景齐了一次性组装,与 JIT 逐页热升级矛盾(jit.md 分工条)。
- **ManimGL(3b1b/manim)**——否决:与 ManimCE 混装冲突,环境唯一线已锁 CE。
