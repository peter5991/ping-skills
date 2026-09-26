# 案例网址登记册(防遗忘)

> 用户提供过的所有网页/3D 学习案例的 URL 总表。**以后每给一个新案例,先在这里登记一行,再决定是否做深潜萃取。**
> 登记格式:名称 | URL | 风格/类型 | 技术栈 | 收录日期 | 学什么 | 深潜文件(无则 —)

## 3D / WebGL 案例

| 名称 | URL | 类型 | 技术栈 | 收录 | 学什么 | 深潜 |
|------|-----|------|--------|------|--------|------|
| Threejs-Punk | https://github.com/anshul360/threejs-punk (demo: https://threejspunk.vercel.app/) | 赛博朋克雨巷漫游 | Three.js r185 WebGPU + TSL、three-mesh-bvh、GSAP | 2026-09-26 | factory 架构、性能预算纪律、GPU 碰撞雨、湿地面反射、TSL 模式 | threejs-punk.md |
| AutoPiano 3D 钢琴 | https://www.autopiano.cn/zh-TW/3d (站: https://www.autopiano.cn/,抓包须带 Referer) | 可交互 3D 乐器 | Three.js WebGL + Tone.js,Nuxt SSR 懒加载 | 2026-09-24 | 程序化建模、弹簧物理按键、Raycaster 白名单拾取、采样音频 | ../case-autopiano-3d.md |
| rocksdanister/rain | https://github.com/rocksdanister/rain | 玻璃雨滴 shader | WebGL shader(BigWings 风格) | 2026-09-26 | 程序化水滴/拖尾/卫星滴;threejs-punk 车身雨滴的原始出处,移植须保留 credit | 见 threejs-punk.md §5 |
| WebCraft (Kaigen) | https://github.com/Kaigen-Technologies/kaigen-minecraft-opus-5-5 | 体素沙盒(Minecraft 式) | C + WASM + WebGPU(Kaigen 引擎,闭源 beta),GLSL 单源多端 | 2026-09-26 | 体素世界架构(chunk 流式/光照洪泛/网格化)、完整延迟渲染管线、全程序化内容(零美术资产) | webcraft-kaigen.md |
| iamtechartist(作者合集) | https://github.com/iamtechartist | Three.js 案例作者主页(17 个案例,demo 均在 iamtechartist.github.io/<仓库名>) | Three.js,部分 TSL/WebGPU、WebGL2 raymarching | 2026-09-26 | 程序化场景/水体模拟/机械教学案例集;**AI 对话式开发工作流的完整标本**(遥测接口/自验收断言/双实现镜像) | iamtechartist-ai-cases.md |

## 动效 / 风格案例(9 站 Awwwards 实测 + 衍生)

| 名称 | URL | 类型 | 收录 | 学什么 | 深潜 |
|------|-----|------|------|--------|------|
| Paolo Vendramini | https://paolovendramini.com | 作品集 | 2026-09-22 | 全屏 OGL/three 作品墙、drag/wheel 惯性 | ../techniques.md |
| obys agency | https://obys.agency |  agency 站 | 2026-09-22 | 全站 lerp 手感、滚动叙事 | ../techniques.md |
| seventeen agency | https://seventeenagency.com | agency 站 | 2026-09-22 | scramble 文字、UnicornStudio hero shader、页面转场(barba) | ../techniques.md |
| Camille Mormal | https://camillemormal.com | 作品集 | 2026-09-22 | 纯 vanilla 75KB 做到 SOTD;遮罩 reveal、SVG 描边、跟随预览 | ../techniques.md |
| cipher.tv | https://cipher.tv | 产品站 | 2026-09-22 | scramble(hover)、blend-mode 混合层 | ../techniques.md |
| Pacome Pertant | https://pacomepertant.com | 作品集 | 2026-09-22 | lerp 出现 44 处的阻尼教科书、spring 缓动、SplitText、three Points 粒子 + Raycaster 扰动 | ../techniques.md |
| Justine Soulié | https://justinesoulie.fr | 作品集 | 2026-09-22 | SVG 进度环预加载、taxi.js 转场、hover 图片流动扭曲 shader | ../techniques.md |
| siena.film | https://siena.film | 影像站 | 2026-09-22 | data-roll 文字翻转、data-parallax 范式 | ../techniques.md |
| Stefan Vitasovic | https://stefanvitasovic.dev | 作品集 | 2026-09-22 | 滚动叙事编排 | ../techniques.md |
| Dala(暗色虚空极简) | https://dala.craftedbygc.com (refero 存档: https://styles.refero.design/style/e5f5f8cf-e68d-4ed1-bbf5-6b67569af648) | 风格线 | 2026-09 | "黑色作为设计材料"、三角形结构粒子"大脑"、200 超细字重 | ../style-references.md |
| peter5991.github.io(自有落地) | https://peter5991.github.io | 个人站 | 2026-09 | Dala 粒子的 MOF 晶格适配(~1000 点 / 1400 边,60fps)——自有改写过验证 | ../techniques.md T0-粒子场 |

## 登记规则

1. **URL 失效不慌**:获奖站改版频繁,失效时先在 refero.design / awwwards 存档找备份,再把新地址补进表(旧地址保留并标注失效)。
2. **"学什么"只写一句话**:详细萃取永远落在深潜文件里,本表只做索引。
3. **同类案例够 3 个才升级**:单一案例只登记;同类满 3 个时考虑在 style-references.md 开一条风格线,或在本文件夹加深潜文件。
4. 3D 案例的深潜文件放本文件夹(`threejs-cases/`);非 3D 的按既有位置(techniques.md / style-references.md / case-*.md)。
