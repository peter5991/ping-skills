# 已核实库清单（版本 / 许可证 / 本地化方式）

> 版本与许可证核实日期：2026-09-04（npm registry 实时查询 + 官方公告）。
> 引入此清单之外的新库时，必须重新核验版本、许可证、离线体积，并更新本文件。

## 核心栈

| 库 | 版本 | 许可证 | 用途 | 本地化文件 |
|---|---|---|---|---|
| Three.js | 0.185.1 | MIT | 3D 场景（WebGL） | `build/three.module.min.js` + `build/three.core.min.js`（ESM，两文件缺一不可） |
| GSAP | 3.15.0 | 免费商用（2025-04 Webflow 收购后全部免费，含原 Club 插件） | 时间轴、滚动叙事 | `dist/gsap.min.js`、`dist/ScrollTrigger.min.js` |
| ECharts | 6.1.0 | Apache-2.0 | 动态数据图表 | `dist/echarts.min.js` |
| reveal.js | 6.0.1 | MIT | 分页演示框架 | `dist/reveal.js`、`dist/reveal.css`、`dist/theme/black.css` |

## 辅助库（按需）

| 库 | 版本 | 许可证 | 用途 | 本地化文件 |
|---|---|---|---|---|
| Lenis | 1.3.26 | MIT | 平滑滚动（配 ScrollTrigger） | `dist/lenis.min.js` |
| Anime.js | 4.5.0 | MIT | 轻量补间（GSAP 之外的小件动效，避免并存） | `dist/bundles/anime.umd.min.js` |
| Swiper | 14.2.0 | MIT | 触摸滑动/轮播 | `swiper-bundle.min.js` + `swiper-bundle.min.css` |
| lottie-web | 5.13.0 | MIT | AE 导出 JSON 动画播放 | `build/player/lottie.min.js` |
| tsParticles | 4.4.0 | MIT | 粒子特效 | `tsparticles.bundle.min.js` |
| PixiJS | 8.20.1 | MIT | 2D WebGL 高性能特效 | `dist/pixi.min.js` |
| Rough.js | 4.6.6 | MIT | 手绘风图形/图表 | `bundled/rough.js` |

## 排除项

| 库 | 原因 |
|---|---|
| p5.js | LGPL-2.1，商用交付不友好 |
| particles.js（旧） | 已停更，用 tsParticles 替代 |
| AOS / ScrollReveal | 滚动入场用原生 Intersection Observer + CSS 即可，避免多滚动控制器并存 |

## 本地化下载

运行 `scripts/fetch-libs.mjs`（Node 18+，需联网执行一次）：

```bash
node scripts/fetch-libs.mjs <目标目录>          # 下载全部核心栈
node scripts/fetch-libs.mjs <目标目录> gsap lenis   # 只下载指定库
```

脚本按本文件的版本号从 jsDelivr 的 npm 镜像取文件（版本锁定，可复现），下载后断网不再依赖网络。产物中引用本地相对路径，例如：

```html
<script src="./libs/gsap.min.js"></script>
<script src="./libs/ScrollTrigger.min.js"></script>
```

Three.js 为 ESM：

```html
<script type="module">
  import * as THREE from './libs/three.module.min.js';
</script>
```
