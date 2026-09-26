# 手法分级库(9 个 Awwwards 获奖站实测萃取)

> 来源:2026-09-22 对 paolovendramini.com / obys.agency / seventeenagency.com / camillemormal.com / cipher.tv / pacomepertant.com / justinesoulie.fr / siena.film / stefanvitasovic.dev 的源码实测(库指纹 + 实现解构)。
> 分级原则:**能低不高**——T0 能办的不上 T1,T1 能办的不上 T2。
> 每项:实现要点 + 代码骨架 + 来源站 + 适用场景 + 滥用红线。

## T0 — vanilla 零依赖(优先使用)

### T0-1 遮罩逐行/逐字入场 ★九站共通
容器 `overflow:hidden`,内层 `translateY(105%)→0`,逐行 delay 递增。长内容逐行拆,短标题逐字/逐词拆。
```html
<span class="line"><span class="inner">第一行标题</span></span>
<style>
.line{display:block;overflow:hidden}
.inner{display:inline-block;transform:translateY(105%);animation:rise .6s cubic-bezier(.22,1,.36,1) forwards}
.line:nth-child(2) .inner{animation-delay:.12s}
@keyframes rise{to{transform:translateY(0)}}
</style>
```
- 滚动触发时把 animation 换成 Intersection Observer 加 class,**一次性**,播完常驻。
- 来源:全部 9 站。红线:长段落不拆字;delay 总长控制在 1s 内(参 motion-tokens.md)。

### T0-2 scramble 文字扰动
字母随机洗牌逐位归位,~30 行 JS。load 版做标题入场,hover 版做导航点睛。
```js
function scramble(el, text, dur = 800) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ01#$%';
  const t0 = performance.now();
  (function tick(now) {
    const p = Math.min((now - t0) / dur, 1);
    const n = Math.floor(p * text.length);
    el.textContent = text.slice(0, n) + [...text.slice(n)].map(c => c === ' ' ? ' ' : chars[Math.random() * chars.length | 0]).join('');
    if (p < 1) requestAnimationFrame(tick);
  })(t0);
}
```
- 来源:cipher.tv(hover)、seventeenagency(load)。GSAP 栈内可用 ScrambleTextPlugin 平替。
- 红线:一页一处,只给主标题/导航;正文不用;中文按字切分。

### T0-3 roll-over 文字 hover
双层文字叠放,hover 时整体上移一行,下层(可换色)露出。纯 CSS。
```html
<a class="roll"><span class="roll-box"><span>关于我们</span><span>关于我们</span></span></a>
<style>
.roll{display:inline-block;overflow:hidden;height:1.2em}
.roll-box{display:block;transition:transform .35s cubic-bezier(.22,1,.36,1)}
.roll-box span{display:block;height:1.2em}
.roll:hover .roll-box{transform:translateY(-1.2em)}
</style>
```
- 来源:siena.film(data-roll)。适用:导航、链接列表。红线:行高必须显式固定,否则错位。

### T0-4 mix-blend-mode:difference 固定 UI
固定导航/logo 一行 CSS,滚过任何底色自动反色,暗色页天然适配。
```css
.site-nav{position:fixed;mix-blend-mode:difference;color:#fff}
```
- 来源:cipher.tv。红线:blend 层内不放图片/复杂背景;低端机实测。

### T0-5 SVG 描边自绘
`stroke-dasharray` + `stroke-dashoffset` 从全长收到 0,纯 CSS 或 rAF。多段 path 拆开 delay 错峰,叙事顺序 = 绘制顺序。
- 来源:camillemormal、siena.film。适用:logo 绘制、签名、曲线/示意图、进度环(预加载器)。
- 红线:含 fill 的图形在描完后再淡入 fill;别给持续循环。

### T0-6 lerp 阻尼(一切手感的底层原语)
```js
let cur = 0;
function raf() { cur += (target - cur) * 0.12; el.style.transform = `translateY(${cur}px)`; requestAnimationFrame(raf); }
```
- 用途:自定义光标、跟随预览、视差、手写平滑滚动。来源:9 站全部(obys/camille 全站手感都建立在此)。
- 系数表见 motion-tokens.md;红线:趋近判断要有截止阈值(`< 0.1` 时吸附目标值),否则永远微调。

### T0-7 自定义光标
固定 div + lerp 跟随 + hover 状态切换(放大/出文字/出图)。
- 来源:6/9 站。**仅屏幕端展示页**;投影课件/工具页禁用(指针可见性优先,且远程演示软件常不渲染自绘层)。
- 红线:必须保留原生 `cursor` 兜底(自绘层是增强不是替代);不挡点击(`pointer-events:none`)。

### T0-8 预加载器
百分比计数 + 数字遮罩上滚(camille:`translate3d(0,300%,0)→0`),或 SVG 进度环(justinesoulie),资源 onload 后盖层淡出。
- **仅在确有重资源(大图集/视频/WebGL 场景)时做**;单文件轻页不做(自造等待感是负资产)。
- 红线:必须有真实进度依据(已加载资源计数),假进度条不做;超时要兜底放行。

### T0-9 鼠标跟随图片预览
作品列表 hover → 预览图 div 跟随鼠标(lerp 阻尼),leave 淡出。
- 来源:camillemormal、obys、seventeenagency。适用:作品/案例列表。红线:预览图 `pointer-events:none`;移动端降级为列表内嵌图。

### T0-10 视差(元素差速)
滚动值 × 系数映射到 `translateY`,只动 transform;声明式写法:`data-parallax="0.3"` + 一个总初始化函数扫 DOM。
- 来源:siena.film(data-parallax 范式)。红线:已引 GSAP 时统一交给 ScrollTrigger scrub,不另写 scroll 监听(红线 #1);系数 ≤ 0.5,反向视差慎用。

### T0-11 弹簧缓动 hover
`cubic-bezier(.34,1.56,.64,1)` 类 spring 曲线做 scale/rotate 微交互;或手写胡克定律 rAF(~20 行)。
- 来源:pacomepertant(--ease-spring)。适用:logo hover 弹出标签、卡片反馈。
- 红线:**克制**——overshoot 只给小件微交互,入场编排与滚动叙事保持 ease-out 类(无回弹);一页 spring 不超过两三处。

### T0-12 声明式动效属性(siena 范式)
`data-reveal` / `data-delay` / `data-parallax` / `data-cursor` 标注元素,一个 init 函数统一扫描接管——动效系统与内容解耦,页面即配置。
- 适用:多页站点保持动效一致性时。单页小作品不必抽象。

### T0-13 结构粒子场(晶格/星座主视觉)
Canvas 2D 手写"有拓扑的粒子场":3D 点阵(晶格/网络/轨道)缓速自转投影,节点画描边三角形、预计算邻接边画细线,深度决定透明度——比随机粒子云多"结构感",是 Dala 式暗色虚空风的签名主视觉(风格规格见 style-references.md)。
```js
// 骨架:pcu 晶格 → 边表预计算 → 每帧只做旋转投影
const rot = {cy:Math.cos(a), sy:Math.sin(a), cx:Math.cos(b), sx:Math.sin(b)};
// 逐点:x1=x*cy-z*sy; z1=x*sy+z*cy; y1=y*cx-z1*sx; z2=y*sx+z1*cx;
//      persp=FOCAL/(FOCAL+z2); screen=center+x1*S*persp; alpha 随 z2 衰减
```
- 来源:dala.craftedbygc.com(三角形粒子"大脑");已落地 peter5991.github.io(MOF 晶格适配,~1000 点 / 1400 边,60fps 无压力)。
- 手感:鼠标视差用帧率无关 lerp(k≈2.2),自转 ≤ 0.05 rad/s;染色节点 ≤ 10%。
- 红线:背景层限定、一页一处,文字对比度独立成立;**静态/降级渲染必须在 resize 后重绘**(canvas 改尺寸即清 buffer,见 verification.md 工程陷阱);`document.hidden` 停 tick;节点规模桌面 ≤1500,移动端减半。

## T1 — GSAP + Lenis 级(本地化,版本见 libs.md)

### T1-1 Lenis 惯性滚动
```html
<script src="./libs/lenis.min.js"></script>
<script>
const lenis = new Lenis({ lerp: 0.1 });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(t => lenis.raf(t * 1000));
</script>
```
- 来源:5/9 站。适用:滚动叙事长页。红线:分页演示/工具页不引;与 ScrollTrigger 接线照抄上文,缺一不可。

### T1-2 ScrollTrigger pin/scrub 滚动叙事
整页即一幕:pin 住场景,滚动进度驱动时间轴。来源:pacomepertant、seventeenagency、obys(自研等价物)。
- 红线:滚动职责全归 ScrollTrigger(红线 #1);每个 pin 段落无 JS 降级时内容顺序仍成立。

### T1-3 stagger 级联入场
`gsap.from(items, {y: 24, opacity: 0, stagger: 0.06, ease: 'power3.out'})`。卡片组/列表的标准入场。
- 红线:vanilla 能写(T0-1 + delay)就不引库;stagger 间隔表见 motion-tokens.md。

### T1-4 惯性拖拽
Draggable + InertiaPlugin(`inertia: true`):轮播、滑块、可拖作品墙,带余振。
- 来源:seventeenagency。红线:拖拽区必须也有点击/滚轮替代路径(可访问性)。

### T1-5 色块页面转场
绝对定位色块组 `scaleY: 0→1→0` 或 translate 序列盖住视口再揭开,GSAP 20 行内。SPA 配合 barba/taxi,单页多屏可直接用。
- 来源:justinesoulie(transition-blocks)、siena(taxi.js)、seventeenagency(barba)。
- 红线:转场 ≤ 0.8s;仅多视图应用需要,单页落地页不做(为转场而转场是纯装饰)。

### T1-6 SplitText 逐词/逐字
GSAP SplitText 拆词拆字,配 stagger/scroll 步进。来源:pacomepertant(SplitText 3.13)、paolovendramini。
- 红线:T0-1 手写拆行已覆盖 80% 场景;只有需要逐词 scrub/复杂时序才动插件。

## T2 — WebGL 级(最后手段,非起点)

### T2-1 粒子背景
three.js Points 粒子场 + Raycaster 指针扰动(pacomepertant 招牌);降级方案:Canvas 2D 手写粒子(数百个以内完全够)。
- 红线:hero/背景层限定,一页一处;文字层对比度必须独立成立(粒子全黑也可读);`document.hidden` 时停 tick。

### T2-2 图片扭曲 shader
单 quad fragment shader(noise + uv 偏移),hover 时图片流动扭曲。justinesoulie/camillemormal 招牌;OGL(轻量)或裸 WebGL 约百行。
- 红线:仅旗舰展示页;**必须提供 CSS 平替降级**(scale + clip-path 视差),WebGL 失败时用降级渲染。

### T2-3 shader 氛围背景
全屏 WebGL2 fragment shader(噪声/流体渐变)做 hero 氛围。来源:seventeenagency(UnicornStudio)、pacomepertant。
- 红线:同 T2-1;单文件离线场景手写 shader 内联,不引引擎。

### T2-4 WebGL 拖拽作品滑块
全屏 OGL/three 渲染作品墙,drag/wheel 惯性驱动(paolovendramini 招牌)。
- 红线:实现成本高,仅作品集旗舰页;评估"生成/交付速度硬约束"时首先砍掉的就是它——T0-9 跟随预览 + T1-4 惯性拖拽可近似 80% 观感。

### T2-5 程序化 3D 交互物件(乐器/产品拆解)
Three.js 图元代码拼装物件(零模型资产)+ 可动部件挂 pivot Group + 阻尼弹簧驱动 + Raycaster 白名单拾取;换肤 = 材质调色板切换。完整参数与代码骨架见 `references/case-autopiano-3d.md`(autopiano.cn/3d 实测:88 键钢琴全程序化建模,按键弹簧 k=205/145、镜头预设 1.05s ease-out cubic、Tone.js 采样发声)。
- 适用:"可上手玩"本身就是卖点的页(虚拟乐器、产品交互展示)。红线:形态不规则的有机物件别程序化,用 glTF;先按 T2 总红线问"要不要 3D"。

### T2 工程要点(motion-web 并入)

- **长焦是画面感的单点杠杆**:fov ≈ 26 压缩纵深,近物与远景剪影相接;纵深靠遮挡剪影咬合读,不靠雾和视差速率(各元素"大近小远各站各的"= 沙盘感)。
- **"拼接感"是色温 bug 且可测量**:打印每批资产的 mean R−B,离群批用一个 light 乘子纠回,别去修边缘羽化。
- **高频细节随视距衰减**防闪烁:`exp(-viewZ × 0.028)`(镜面/闪光 0.05);风的相位来自世界坐标(相邻植株一起倒)而非随机种子,两轴异频异幅——随机相位 = 静电噪点。
- **Three.js 三个静默炸点**:注入 GLSL 的数必须格式化 int→float(`6` → `"6.0"`,否则整批实例消失无报错);自定义 ShaderMaterial 补 `#include <tonemapping_fragment>` 与 `colorspace_fragment`;DepthTexture 只能 NEAREST(LINEAR 采样全 0)。
- **纹理复用**:结构(grain 形状)可复用,浓度不可;一张白图喂多层(RGB 恒定、信息全在 alpha、每层材质色梯度 0.015·i)可替代 shader 雾。
- **大场景流式**:激活窗口不对称(前方 4.5 屏、后方 3 屏);扫描协程每帧 ≤4.17ms 让出主线程;dispose 三件套(geometry/material/texture),load 回调守 disposed 旗(快滚时纹理贴到死 mesh 的泄漏只在这里防)。

## 明确不做清单(各场景)

| 手法 | 不做场景 | 原因 |
|---|---|---|
| 自定义光标(T0-7) | 投影课件、工具页、远程演示 | 指针可见性优先;远程软件不渲染自绘层 |
| 预加载器(T0-8) | 轻量单文件页 | 自造等待感 |
| 页面转场(T1-5) | 单页落地页、课件(软件负责切页) | 纯装饰 |
| hover 音效 | 课堂、办公场景 | 打扰;需用户手势解锁音频,得不偿失 |
| 弹簧缓动(T0-11) | 入场编排、滚动叙事 | overshoot 与"ease-out 类"主基调冲突,只给小件微交互 |
| WebGL 全家桶(T2) | 有生成速度硬约束的页面、低端设备 | 成本高,T0/T1 可近似 80% 观感 |
