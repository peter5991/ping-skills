# 33 项 Web 动画效果选型清单

> 来源：`animation-showcase.html`（可运行参考页，**CDN 依赖，禁止直接交付**）。
> 每项给出：推荐实现（按红线收敛后的单一主控方案）、性能注意点、适用场景。
> 图例：✅ 推荐采用 · ⚠️ 有条件采用 · ❌ 排除/仅参考

## 一、演示骨架与滚动叙事

| # | 效果 | 推荐实现 | 性能/边界 | 适用场景 |
|---|---|---|---|---|
| 01 | 分页翻片演示 | ✅ reveal.js（Fragment 逐条出现、Auto-Animate） | 原生 JS 可运行，分页演示首选起点 | 网页 PPT、路演分页稿 |
| 04 | 滚动驱动动画（pin/scrub） | ✅ GSAP + ScrollTrigger | 长页叙事核心；滚动职责全归它，不要再加 AOS/ScrollReveal | 滚动叙事长页、数据故事 |
| 09 | 平滑滚动 | ✅ Lenis（配 GSAP ScrollTrigger） | 仅滚动叙事长页引入；分页 demo 不需要 | 长页手感增强 |
| 20 | CSS 滚动驱动动画 | ⚠️ `animation-timeline: view()` 纯 CSS 方案 | Chrome 115+；必须写 `@supports` 降级为最终状态 | 简单入场且确定现代浏览器 |
| 25 | 视差滚动 | ⚠️ 手写 JS 只改 `transform`，或并入 GSAP scrub | 页面已用 GSAP 时统一交给 GSAP，不要另写 scroll 监听 | 落地页深度感 |

## 二、科技风氛围

| # | 效果 | 推荐实现 | 性能/边界 | 适用场景 |
|---|---|---|---|---|
| 07 | 3D 场景/线框模型 | ✅ Three.js + GSAP 驱动镜头 | 只用于增强主题的关键段落；低端机实测帧率 | 科技风开场、产品模型 |
| 12 | 粒子系统（星空/气泡/交互） | ✅ tsParticles（少量粒子）/ PixiJS（大量粒子） | 旧 particles.js 已停更勿用；粒子数控制在可实测范围 | 背景氛围、互动点缀 |
| 18 | 大量 2D 精灵高性能动画 | ✅ PixiJS（WebGL） | "哇塞"瞬间专用，不必每页都用 | 开场粒子汇聚、数字爆发 |
| 16 | 创意编程生成艺术 | ❌ p5.js（LGPL） | 商用交付排除；同类需求改手写 Canvas 2D（见 #21） | — |
| 21 | 手写 Canvas 2D 粒子 | ✅ 原生 Canvas 2D | 零依赖完全可控；注意粒子生命周期回收 | 定制化小特效 |
| 27 | 鼠标跟随光晕 | ✅ 手写 JS + rAF 缓动 | 只改 `transform`（showcase 旧实现改 `left/top`，应改 `translate`） | 科技风光标效果 |
| 28 | 文字乱码解码 | ✅ 手写 JS（~30 行） | 零依赖；注意中文按字符切分 | 黑客/科技风标题 |
| 19 | CSS 3D 立方体/卡片翻转 | ✅ 纯 CSS `preserve-3d` | 零依赖 | 小件 3D 点缀 |
| 22 | clip-path 形状变形 | ⚠️ 纯 CSS 一次性揭示可用 | 持续循环动画有绘制成本，需实测 | 图片揭示、转场 |
| 23 | filter 滤镜动画 | ⚠️ 短促点缀可用 | blur/brightness 持续动画开销大，避免循环 | 氛围强调瞬间 |

## 三、信息呈现

| # | 效果 | 推荐实现 | 性能/边界 | 适用场景 |
|---|---|---|---|---|
| 02 | CSS @keyframes 循环/入场 | ✅ 纯 CSS（弹跳、流光字、呼吸点） | 不占 JS 主线程，性能最好 | 一切循环氛围小效果 |
| 03 | CSS transition 状态过渡 | ✅ 纯 CSS | 交互反馈标准做法 | hover、class 切换 |
| 05 | stagger 网格交错入场 | ⚠️ Anime.js；已用 GSAP 时用 `gsap stagger` 替代 | 不与 GSAP 并存 | 网格波浪、列表依次入场 |
| 24 | 滚动触发入场 | ✅ Intersection Observer + CSS transition | 原生零依赖性能最佳，优先于 AOS/ScrollReveal | 元素入视口淡入 |
| 29 | Grid + IO stagger 入场 | ✅ IO + CSS transition + `transition-delay` | 纯原生可实现，不必引库 | 功能列表、作品集 |
| 30 | SVG 路径描绘 | ✅ 纯 CSS `stroke-dasharray/offset` | 比 Vivus 更轻量，优先用它 | 折线/图形描绘 |
| 13 | SVG 逐笔描边 | ⚠️ Vivus（参考项） | 仅在 CSS 方案不够时引入，引入前核维护状态 | logo 绘制、签名 |
| 06 | AE 导出矢量动效 | ⚠️ Lottie（lottie-web 本地化） | JSON 与播放器都本地化；适合设计师交付物 | 图标、加载、吉祥物 |
| 14 | 打字机效果 | ⚠️ Typed.js（参考项） | 简单打字可手写 ~20 行 JS 替代 | 标语、代码演示 |
| 32 | CSS 变量动画 | ⚠️ `@property` + keyframes | Chrome 131+，必须降级处理 | 程序化尺寸/颜色变化 |

## 四、交互反馈

| # | 效果 | 推荐实现 | 性能/边界 | 适用场景 |
|---|---|---|---|---|
| 08 | 状态/页面平滑切换 | ⚠️ View Transitions API | Chrome 111+；旧浏览器退化为直接切换（需接受） | PPT 式切屏过渡 |
| 10 | AOS 滚动入场 | ❌ 用 #24 IO+CSS 替代 | 与 GSAP 并存会双重控制滚动 | — |
| 11 | ScrollReveal 滚动入场 | ❌ 同上 | 同上 | — |
| 15 | 触摸轮播/滑动 | ✅ Swiper | 移动端体验好；本地化 css+js | 图片轮播、卡片滑动 |
| 26 | 滚动吸附 | ✅ CSS `scroll-snap` | 零依赖 | 轻量逐张切换 |
| 17 | 弹簧物理回弹 | ⚠️ Popmotion（参考项）；或手写（见 #33） | React 栈用 Motion 的弹簧即可 | 弹性交互反馈 |
| 31 | WAAPI 播放控制 | ✅ 原生 `element.animate()` | 需播放/暂停/倒放/调速时优先于引库 | 可编程局部动效 |
| 33 | 手写弹簧物理 | ✅ rAF + 胡克定律（~20 行） | 零依赖；参数 `k`/阻尼按手感调 | 点击弹跳、拖拽回弹 |

## 快速选型口诀

1. 循环氛围/交互反馈 → **纯 CSS**
2. 入视口出现 → **Intersection Observer + CSS**
3. 滚动驱动叙事 → **GSAP + ScrollTrigger**（全页滚动职责归它一家）
4. 3D → **Three.js**，镜头交给 GSAP
5. 大量 2D 特效 → **PixiJS**
6. 播放控制/物理手感 → **WAAPI 或 20 行手写 rAF**
