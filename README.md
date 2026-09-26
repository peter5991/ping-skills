# ping-skills

个人维护的 Claude Code skills 合集。每个 skill 是一个独立文件夹，包含 `SKILL.md`(入口，含 frontmatter 与工作流程）和可选的 `references/`(按需加载的详细参考)。

## Skills 一览

| Skill | 用途 | 触发场景 |
|---|---|---|
| [brainstorm](brainstorm/) | 结构化头脑风暴：强制先澄清意图，再以正向/中立/反向三视角逐轮碰撞，收敛为综合建议 | 讨论方案、发散思考、分析决策、评估想法 |
| [ppt-pyramid-planner](ppt-pyramid-planner/) | 三层金字塔模型规划 PPT 内容结构：一句话核心主张 → MECE 支撑论点 → 逐页大字文案 | 做 PPT、路演稿、答辩稿、工作汇报、列大纲 |
| [frontend-craft](frontend-craft/) | 全栈前端设计规范：布局/排版/配色/动效选型与执行标准,T0/T1/T2 手法分级库、手感参数表、Three.js 通用规范与 3D 案例库（取代 html-motion-craft) | 制作网页/落地页/作品集/展示页/路演页，讨论某个效果或动效怎么实现 |
| [bp-roadshow-guide](bp-roadshow-guide/) | 创业/双创比赛商业计划书(BP)撰写与路演设计指导：评审逻辑、BP 17 模块、路演全流程、PPT 与网页双载体规范，附自检清单 | 商业计划书、网评材料、参赛 PPT、路演设计、路演网页 |
| [competition-deck](competition-deck/) | 16:9 翻页式「类 PPT」网页制作：10 种比赛页型目录、浅色竞赛母版 token、Codex CLI 配图管线，比赛/通用双模式 | 比赛 PPT 网页、路演网页、参赛演示页、PPT 式 HTML、幻灯片网页 |
| [lesson-prep](lesson-prep/) | 备课预制课件页工作流：滚动叙事解禁、GSAP/Lenis 本地库、七配方武器库、探针验收、课程登记 | 备课、照教案做网页、预制课件页 |

> 注:competition-deck 与 lesson-prep 源自私有项目(课堂 AI 助教),文中部分路径(如 `assets/lesson/libs/`、`electron/agent/pagegen-prompt.ts`)相对该项目仓库,移植使用时需按自身环境调整。

## 安装

把需要的 skill 文件夹复制到 Claude Code 的 skills 目录：

```powershell
# Windows(用户级,所有项目可用)
Copy-Item -Recurse bp-roadshow-guide "$env:USERPROFILE\.claude\skills\"
```

```bash
# macOS / Linux
cp -r bp-roadshow-guide ~/.claude/skills/
```

复制后新会话自动生效；描述中列出的触发词出现时会自动调用，也可用 `/skill-name` 显式调用。

## 约定

- 每个 skill 自包含、聚焦单一工作流；
- `SKILL.md` 只放入口流程与路由，长篇参考内容放 `references/` 按需加载；
- 仓库公开，请勿提交敏感信息（令牌、密钥、私人路径）。
