---
name: lesson-prep
description: "备课预制页制作工作流:照教案在 Claude Code 中制作高级感课件页(滚动叙事解禁、GSAP/Lenis 本地库、七配方武器库、探针验收、课程登记)。当用户说'备课''照教案做网页''做预制课件页''lesson prep',或要求用高级感动效制作课件时使用。备课模式判据 = 无激活课程:本 skill 管 Claude Code 侧(完整高级感);软件内无课程的 make_page 也算备课模式,走 pagegen 变体提示词——教师原话带'备课/预制' = 重备课(GSAP/Lenis 解禁,与本 skill 同级),不带 = 轻备课(vanilla)。临场页(有激活课程)不归本 skill 管。"
---

# lesson-prep — 备课预制页工作流

把教案变成**备课模式**课件页:mark 可省、滚动叙事/强制线性解禁、可用本地 vendor 库(GSAP 全家桶 + Lenis)。与软件内临场生成分工见 CLAUDE.md 课件制作约定"双模式"条——**临场页不要走本流程**(那是 pagegen 的活,R0~R8 vanilla 配方)。

## 不可破的红线(比临场页松,但不是没有)

1. **离线**:只允许引用 `assets/lesson/libs/` 下的本地库(相对路径),禁任何 CDN/外部 URL。图片走 assets/ 人工验收流程,不写代码生图。
2. **投影可读**:深色底(向主色调微偏,不纯黑)、大字、高对比、三米外可读;中文字体只用系统栈("Microsoft YaHei","PingFang SC",system-ui)。
3. **不编造数据**:页面每个数字必须有出处(教案/公式算对)。
4. **反 AI 味**:先读 `.claude/skills/hallmark`;单主色调、禁紫蓝渐变/渐变标题/emoji 当图标;结构按内容选型,同课程相邻页不同骨架。
5. **软件定位 = 辅助**:页面是教师讲解的教具,不是自动播放的片子——默认教师滚动/点击驱动,自动播放的长编排要克制。

## 七配方武器库(2026-09-19 四参考站解构萃取,数据见 log.md)

库接线照抄 `assets/lesson/libs/README.md`;`gsap.registerPlugin(...)` 别忘了。

| # | 配方 | 实现要点 | 用法红线 |
|---|---|---|---|
| P1 | 逐字扰动标题 | ScrambleTextPlugin,`chars:"01"` 或片假名,加载即播一次,~1.2s | 一页一处,只给主标题或结论框 |
| P2 | SVG 描边自绘 | DrawSVGPlugin:函数曲线/受力箭头/电路图 `drawSVG:0→100%`,scroll 或 click 驱动 | **教学契合度最高**,优先于装饰性配方;是 R3 手绘圈注的完全体 |
| P3 | 滚动色彩流转 | ScrollTrigger scrub 驱动 CSS 变量(`--accent` 的 lightness/hue 微调),参考站实测颜色变化是主角(shelby 1141 次) | **同一色相族内流转**,不破单主色调纪律 |
| P4 | 逐词点亮揭示 | SplitText 拆词,未讲词 `opacity:.2`→点亮 `1`,按阅读序,挂 scroll 或 click 步进;vanilla 平替 = ENGINEER_PROMPT R9 逐字点亮(逐字粒度中文更顺,零库依赖,临场页也能用) | 与讲解节奏同步;长段落不用 |
| P5 | Lenis 惯性滚动 | `new Lenis({lerp:.1})` + rAF 循环;与 ScrollTrigger 接线:`lenis.on('scroll',ScrollTrigger.update)` | **备课页限定**;临场页禁用(与 mark 自动滚动冲突) |
| P6 | shader 氛围背景 | hero 独占一块 WebGL2 fragment shader(噪声/流体渐变),零依赖手写,机制参考 output/ref/motion-web/cases/ink-crowd | hero 限定;文字层对比度必须独立成立(shader 全黑也要可读) |
| P7 | 惯性拖拽 | Draggable+InertiaPlugin:滑块/旋钮带余振,`inertia:true` | 控件大、读数大(tabular-nums),三米外可操作 |

一页最多两处"重配方"(P1/P2/P6),其余做点缀;先设计静帧再挂动效(动效全关截图也要成立)。

## 工作流程

1. **读教案**:`assets/lesson/<课程>/` 下的教案.md/index.md,确认本课要哪些页、每页讲什么、触发语怎么接线。
2. **规划**:页清单 + 每页叙事弧(参考 motion-web `references/choreography-arc.md`)+ 骨架选型(相邻页不同骨架)+ 主色 + 配方编号,写成一页计划**先给负责人过目**再动手。
3. **制作**:逐页单 .html 落 `assets/lesson/<课程>/`(备课页不放 generated/,那是临场页缓存);库引用相对路径按页面深度算对。
4. **验收**(每页必过):
   - playwright 逐区块截图(范式 `output/test/cn-lesson-shot.cjs`)+ **console 零报错**
   - 交互探针:每个交互组件写一个确定性断言(拖滑块后读数/波形真的变了吗;click 步进幂等吗),照 motion-web `scripts/verify_case.py` 思路,脚本落 `output/test/`
   - 动效全关静帧过目(hallmark 纪律)
5. **人工过目**:截图+录屏给负责人,过了才登记。
6. **登记**:课程 README(页清单;有锚点才登记锚点,备课页可省)+ 教案 `[action:show ...]` 接线 + 教师提词卡更新。验收证据(截图/探针输出)留 output/test/。

## 参考资源

- `output/ref/motion-web/`(本地克隆,不入库;缺失则重克隆 https://github.com/feitangyuan/motion-web)——pattern-recipes.md / build-mode.md / design-slop.md / verification-harness.md;写 GSAP 前必读 build-mode.md 的 Failure Patterns 表
- 解构原始数据:`output/ref/motion-web/data/structure-bank.json`(四参考站)
- 验收范式:`output/test/cn-lesson-shot.cjs`
