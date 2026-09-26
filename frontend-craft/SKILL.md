---
name: frontend-craft
description: 全栈前端设计规范——布局/排版/配色/动效/交互的选型与执行标准,萃取自 9 个 Awwwards 获奖站(paolovendramini/obys/seventeenagency/camillemormal/cipher.tv/pacomepertant/justinesoulie/siena.film/stefanvitasovic)的实测解构。当用户要求制作网页、落地页、作品集、展示页、路演页、前端界面,或讨论某个效果/动效/交互怎么实现、怎么做出"高级感"时使用。内置手法分级库(T0 vanilla/T1 GSAP 级/T2 WebGL 级)、手感参数表、33 项效果选型目录、库版本清单与本地化脚本。课件(课堂投影)场景另有专案纪律,走项目侧 lesson-prep/pagegen,不用本 skill。
---

# Frontend Craft — 全栈前端设计规范

制作任何网页/前端界面时按本 skill 执行。目标:**静帧先成立,动效服务内容,断网能开,手感可调**。

## 高级感第一性原理(9 站实测萃取)

1. **阻尼感 = 贵**。lerp 插值是一切高级手感的来源:平滑滚动、自定义光标、跟随预览、视差,全部是对目标值做逐帧趋近(`current += (target - current) * 0.1`),而不是瞬移。pacomepertant 全站 lerp 出现 44 处。
2. **遮罩 reveal 是第一入场手法**。9/9 站共用:文字装进 `overflow:hidden` 容器,内层 `translateY(105%)→0` 逐行/逐字升起。零依赖,vanilla 即可,永远优先于任何库。
3. **克制**。单主色、大留白、超大字;高级感 80% 来自阻尼+遮罩+配色,不来自 WebGL。camillemormal 纯 vanilla 手写 75KB 拿到 SOTD 水准——WebGL 是最后手段,不是起点。
4. **每个可交互元素都有 hover 反馈设计**。roll-over 文字、透明度微降、图片预览跟随、scramble 扰动——交互反馈是"被设计过"和"默认样式"的分水岭。
5. **入场一次性,持续动效最多一两处**。循环氛围(粒子/shader/呼吸)只做背景层,不抢内容。

## 硬性红线(每次执行必查,不可妥协)

1. **一个动画职责只保留一个主控库。** 禁止 GSAP、AOS、ScrollReveal、Anime.js 等多套控制器并存操作同一元素或同一滚动进度。选定了就只用它(AOS/ScrollReveal 永久排除,用 Intersection Observer + CSS 替代)。
2. **动画属性只用 `transform` 与 `opacity`。** 持续动画禁止 `width`/`height`/`top`/`left`;`filter`、`clip-path` 仅在一次性/短促效果中谨慎使用。
3. **所有第三方库本地化交付。** 产物不依赖任何 CDN,断网双击 HTML 必须完整运行。库文件随产物走(本地相对路径或单文件内联);版本只从 `references/libs.md` 清单取,新库先核验再登记。
4. **简单效果优先原生 CSS/JS。** `@keyframes`/`transition`/Intersection Observer 能解决的,不引任何库。T0 手法(见 techniques.md)全部零依赖。
5. **排除项**:p5.js(LGPL)、旧 particles.js(停更,用 tsParticles)。

## 工作流程

1. **判场景**:受众是屏幕端还是投影?展示页还是工具页?有没有既有专案纪律(如课堂课件走 lesson-prep,本 skill 让位)?场景决定手法白名单(如自定义光标/预加载器只适合屏幕端展示页)。
2. **静帧先行**:布局/排版/配色按 `references/design-foundation.md` 先设计到"动效全关也成立"。动效是放大器,不是遮羞布。**用户给定参考网页时**,按 `references/style-references.md` 的解码协议做两层分析(视觉规格 + 实现方式:库指纹/动画 driver/DOM 手法/资产),并查该库有无已收录条目;新风格落地后回写。
3. **动效选型**:先查 `references/techniques.md` 手法分级库(T0 vanilla → T1 GSAP 级 → T2 WebGL 级,能低不高);技术实现拿不准再查 `references/effects-catalog.md`(33 项选型)。**涉及 3D/Three.js 时**先读 `references/threejs-guide.md`,并查 `references/threejs-cases/_index.md` 有无已萃取的同类案例。
4. **手感调校**:时长/缓动/stagger/lerp 系数按 `references/motion-tokens.md` 取值,不凭空写数字。
5. **库本地化**:缺库运行 `scripts/fetch-libs.mjs <目标目录> [库名]`(版本锁定在 libs.md)。
6. **验收**:过文末清单,不通过不交付。

## 参考资源

- `references/techniques.md` — **手法分级库**(T0/T1/T2,每项含代码骨架、来源站、适用场景、滥用红线),先读这个
- `references/case-autopiano-3d.md` — **范本案例**:AutoPiano 3D 钢琴(程序化 3D 建模 + 弹簧物理按键 + Tone.js 采样发声 + Raycaster 拾取,全参数实测)
- `references/threejs-guide.md` — **Three.js 通用规范**(T2 级总指南:渲染器选型/factory 骨架/资产管线/性能预算/材质着色/后处理 + 3D 专项验收清单)
- `references/threejs-cases/` — **3D 案例库**:`_index.md` 登记所有案例网址(新案例先登记再萃取);`threejs-punk.md` 为完整萃取范本(WebGPU+TSL 雨巷:架构/性能预算/GPU 碰撞雨/湿地面反射)
- `references/style-references.md` — **风格解码库**(整条风格线的配色/排版/布局/签名视觉规格 + 适配红线;首条:Dala 暗色虚空极简)
- `references/techniques-showcase.html` — T0 全手法可运行展示页(离线单文件零依赖,手法活标本)
- `references/design-foundation.md` — 静帧层规范:布局骨架/排版/配色/反 AI 味清单 + 获奖站实测基准
- `references/motion-tokens.md` — 手感参数表:缓动曲线、时长区间、stagger 间隔、lerp 系数、帧率无关写法
- `references/choreography.md` — 编排纪律:多动效时间轴排布(一窗口一事件、money frame、静止率)
- `references/verification.md` — 验收工程:数值神谕、探针契约、帧率无关验证、工程陷阱
- `references/effects-catalog.md` — 33 项效果技术选型清单(库决策)
- `references/libs.md` — 已核实库版本/许可证/本地化方式
- `references/animation-showcase.html` — 33 项效果可运行参考页(依赖 CDN,**仅借鉴,严禁直接交付**)
- `scripts/fetch-libs.mjs` — 库本地化下载脚本(Node 18+)

## 验收清单(交付前逐项过)

1. **静帧成立**:动效全关截图,布局/排版/配色依然成立;完工态写在常规 CSS,动效只是"从完工态倒播进来",JS 失效页面照样可读。
2. **断网双击**:所有库与资源本地加载,console 零报错零 404。
3. **单一主控**:无多个库控制同一元素/滚动进度;持续动画只动 `transform`/`opacity`;同一属性只有一个 driver(CSS transition 与 rAF 不混写)。
4. **入场一次性**:入场编排播完常驻完工态;滚动触发的 reveal 用 Intersection Observer(或已选主控库),不重复触发。
5. **编排过检**:多动效页过 `references/choreography.md` 检查单(一窗口一事件、money frame 可截、静止率)。
6. **低性能实测**:DevTools 6x CPU 降速下滚动/动画无明显卡顿;帧率无关写法(乘 dt)抽查。
7. **每个引入的库能回答"为什么是它"**,版本出自 libs.md;新库已核验许可证并回写 libs.md。
8. **有争议效果上数值神谕**:按 `references/verification.md` 写一次性 oracle(一个 oracle 一条投诉),不用肉眼拉锯,禁综合质量分。

## 项目专用约束(定制演示设计服务项目;其他场景忽略本节)

1. **风格优先级**:深色科技风做完整套;学术风/国潮风各出少量样张。深色科技风完整案例必须体现 Three.js 3D + GSAP 滚动叙事 + ECharts 动态图表三件套。
2. **整页生图"大字少字"**:AI 生图页面只保留大标题级文字,小字正文一律后期叠加文本框(HTML 层覆盖真实文字),防止生图糊字。
3. **虚构内容要仿真**:竞赛高频选题 + 毛边数据(非整数)+ 一句话项目背景。
4. **验收对齐项目文档**:`docs/HTML演示技术手段-2026-09-09.md` §9 与 `docs/组件库选型-2026-09-04.md` 是项目侧权威版本;冲突时以项目文档为准并回写修正本 skill。
