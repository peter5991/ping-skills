# 案例:WebCraft (Kaigen) — C/WASM/WebGPU 体素沙盒(完整萃取)

> 来源:2026-09-26 对 https://github.com/Kaigen-Technologies/kaigen-minecraft-opus-5-5 全仓库源码萃取(C 约 1 万行 + 35 个 GLSL shader,三个并行子代理分线精读)。
> 性质:Kaigen Engine(**闭源 beta**)的官方 demo——Minecraft 式体素沙盒,同一份 C 源码编译到 Windows(D3D12)与浏览器(WASM + WebGPU)。**引擎拿不到、代码不能跑也不能直接用;价值全在架构思想与 shader 技巧。**
> 一句话:**这是一份"完整现代渲染管线 + 完整体素引擎"的最小可读实现——每条技巧都标注了 Three.js 对应物,是 threejs-punk(单场景秀技)之外的另一条学习线:系统性世界。**

## 0. 什么时候读这份案例

| 场景 | 读哪节 |
|------|--------|
| 做体素/沙盒/程序化世界(任何引擎) | §2 体素世界 |
| 搭多 pass 渲染管线、排 pass 顺序 | §3 渲染管线 |
| 帧率优化找砍单 | §3.9 性能取舍表 + §4.5 画质预设表 |
| 程序化纹理/音频/图标(零美术资产路线) | §4 |
| 找"这个效果 Three.js 里怎么做" | §6 移植技巧精选 |
| 对比"单场景秀技"与"系统性世界"的工程差异 | §5 与 threejs-punk 对照 |

**前置警告**:项目使用自研 GPU 抽象层 + reverse-z 无限远投影 + 相机相对坐标(世界坐标减相机位置,double 在 CPU、f32 进 GPU)——这三件是大地图不抖的根基,移植时先理解再动手。所有世界=seed+diff 的纯函数式持久化,换 seed 即新世界。

## 1. 架构总览

- **同一份 shader 源码**编译到所有后端(SPIR-V/HLSL 跨编译);所有 pass 共用一个 1024 字节帧 UBO;全屏效果一律全屏三角形(不用 quad)。
- **线程模型 = lock-step round + 原子游标**:所有线程(含主线程)进同一个 job 循环,每轮用原子自增抢 job,轮末 barrier 同步,主线程整合结果再调度下一轮。**全管线零锁**——唯一的同步原语是两个 barrier 和一个原子计数器。job 数组调度期单写、执行期只读。
- **帧结构**:整合上轮结果+GPU 上传 → 流式更新+调度 → 渲染 → 所有 lane 跑 job。计算跟在渲染后面,不占渲染前的关键路径。
- **WASM 降级**:移动端**强制单线程**(SharedArrayBuffer 在手机上不可靠);桌面要 crossOriginIsolated 才走多线程;pipeline 异步编译,未就绪的效果当关闭处理。

## 2. 体素世界

### 2.1 Chunk 数据模型(`wc.h`)

- Chunk = 16×16×256,高度切 16 个 16³ **section**,网格化/版本号/空段跳过全以 section 为粒度。
- 方块**直接 u8 数组**(65536/chunk),无 palette 无 RLE——74 种方块时 palette 是纯开销。光照同尺寸一字节:高 4bit 天光 + 低 4bit 方块光,**无 RGB**。
- 世界索引用 **toroidal 环形网格**(64×64 slot + free list),不用 hash map:O(1)、无 GC、内存硬封顶。卸载半径 < 网格半径一半即安全。
- 方块属性:X-macro 大表展开成 10 张 `u8[256]` **平行查表**(shape/solid/occludes/emission/tint…),查属性 = 一次数组索引。

### 2.2 流式加载(`wc_world.c`)

- wanted 列表 = 玩家为中心半径 r+3 的圆盘,counting sort 按距离排,**优先级纯距离、无视锥**;流水线推进:GEN → LIGHT(需 3×3 邻已生成)→ MESH(需 3×3 邻已打光)。
- **时间预算自适应**:每类 job 成本记滑动平均(α=1/32),每轮能放几个 job = `线程数 × 剩余ms / 估算成本`;预算分档:加载屏 40ms、突发 20ms、稳态=帧空闲 clamp(1.5,12)ms;near-first 时切 4ms 小轮降延迟。
- **防冲突靠 claim 窗口**:3×3 邻域重叠的 job 不得同轮(光照写、网格读会互相踩)。
- **near-first 地平线**:只调度"最近未网格化距离 + 3 chunk"以内的活,远处不浪费。

### 2.3 地形生成(`wc_gen.c`)

- 16 个独立 seed 的 Simplex 场(warp/大陆/侵蚀/山峰/河/温/湿/洞穴…),seed 由 LCG 逐场派生,**逐 chunk 确定性**。
- 列管线:domain warp(fbm 3oct,振幅 45 格)→ continentalness 经 12 点 spline 映射基础高度 → 山 = ridged fbm × smoothstep(侵蚀)→ 丘陵/细节。
- **洞穴优化(重点)**:3D 噪声只在 4 格间距的粗网格(5×5×65)上算,方块级取值**三线性插值**——成本降约 64 倍且洞壁更平滑。
- 树用 **jittered 5×5 格网**放置,跨界树靠 margin 采样 + 越界写入裁剪,每 chunk 独立可重算,消灭 chunk 间依赖。
- 生物群系 = temp/humid 双噪声 + 海拔降温的**决策树**(21 种),不是 MC 的多噪声气候采样器。

### 2.4 光照洪泛(`wc_light.c`,289 行讲完)

- 天光:每列自上而下 level 15 直落、遇 opacity 衰减;**level==15 向下只减 opacity 不减 1**(太阳直射不衰减)。
- 传播 = 3×3 chunk 窗口内 BFS(单调环形队列),出队时光值不增即跳过(标准洪泛去重)。
- **增量更新 = 先退后传**:改一个方块,反向 BFS 把"期望值对不上"的邻居清零(途中发现别的光源照进来的转传播种子),再正向 BFS 两趟(天光/方块光各一)。
- **版本号桥接**:光照写入时 bump 受影响 section 的 `sec_version`,网格层纯被动比对版本决定重网格——**光照系统不知道网格系统的存在**。系统解耦的范本。

### 2.5 网格化(`wc_mesh.c` / `wc_mesh_store.c`)

- 输入 18³ padded 体积(中心 16³ + 邻边一圈);逐面剔除(邻居 occludes 则丢;同类透明互剔);**无 greedy meshing**。
- **顶点格式 = 每 quad 5×u32(20 字节)**:位置 4bit×3 + face + shape + 逐角 AO(2bit)+ 逐角光 + tint,**顶点着色器里展开 4 角(vertex pulling),没有顶点缓冲**。比传统顶点格式省 5–10 倍 VRAM。
- AO = 经典 2 side + 1 corner 采样,`3-(s1+s2+corner)`;光照按非遮挡邻居平均(smooth lighting)。
- **13 桶 counting sort 分 draw**:6 普通朝向 + 6 flagged 朝向(cutout/摇摆/冰)+ other,渲染按桶区间开关特性,不加 draw call。
- **异步容错**:mesh job 记下 sec_version,结果回来时版本过期**直接丢弃**——天然容忍 worker 乱序完成。
- GPU 池:OffsetAllocator 分配 + **retire 延迟释放**(过 N 帧才真回收,CPU 不等 GPU);每帧上传空间不够就拒收结果留待下帧。

### 2.6 物理与持久化(简记)

- 玩家:AABB 逐轴移动 + 子步进(≤0.35 格);**指数趋近加速** `v += (target-v)(1-e^(-k·dt))`,帧率无关;视线 raycast 用 Amanatides & Woo DDA。
- 持久化 = 每 chunk 一个 diff 列表(每条 4 字节),chunk 重生成后立即重放——**世界 = seed + diff**,edits 独立于 chunk 生命周期,卸载不丢玩家改动。

## 3. 渲染管线(`wc_render.c` + 35 shader)

### 3.1 一帧的 pass 序列

```
[一次性] 噪声烘焙(3 张 compute 存储纹理) + 大气 LUT ×2
CPU 粗剔(列/section/面桶,同时服务相机+阴影多视锥)
→ GPU 展开 compute(范围 → 可见 quad 列表)
→ Sky-view LUT ×2(仅角度/高度超阈值重画)
→ Ambient cube(6×1 辐照度,每帧)
→ 阴影 atlas(4 级联各占一象限,只清/只画待刷新级联)
→ G-buffer(全 res 4 RT:albedo/法线×2/光照+AO/材质)
→ SSAO(半 res)
→ 云 march(1/2 或 1/4 res 再砍半)+ 云 temporal(重投影)
→ Deferred lighting(全 res,天空背景也在此画)
→ 水/冰 forward(折射读 scene/depth 拷贝,SSR)
→ 光柱(半 res)→ Atmospherics(高度雾+光柱合成+雨雪)
→ TAA(内嵌上采样,render_scale<1 时 history 直接生在输出尺寸)
→ Bloom down ×6 → 曝光(1×1,采 bloom 第 1 级)→ Bloom up ×5
→ Final(锐化/AgX/暗角/dither/准星)→ swapchain
```

**降级机制**:pipeline 未编译好就当效果关闭;**SSR 依赖 TAA 历史,没 TAA 就连带关 SSR**——效果之间的依赖关系显式编码,不是隐式崩溃。

### 3.2 剔除:CPU 粗剔 + 面桶 + GPU 展开(无 hi-z、无 occlusion)

- CPU 一次遍历同时对所有视锥(相机不透明/半透明/各阴影级联/水面)做列 AABB → section 级视锥测试;**buried 优化**:相机高于地表 8 格时,近景级联跳过地表 22 格以下的 section。
- **面桶剔除**:相机 pass 按 section 相对相机方位丢背向面;阴影 pass 按光向丢背光面(实体方块被自己远面遮蔽);半透明全保留。
- GPU compute 只做"memcpy 式展开"(range → quad 列表),逐 quad 剔除不存在;绘制 = 静态 IB + 实例索引 vertex pulling,一个 pool 一次 draw。

### 3.3 阴影:4 级联 + 跨帧缓存

- 分割 = shadow_distance × {0.07, 0.2, 0.46, 1.0};级联盒**以相机为中心但世界锚定**(光空间 texel 吸附,双精度)——旋转零失效。
- 级联 0/1 每帧重画(带树叶摇摆);**级联 2/3 跨帧缓存**,失效条件:光向量化变化 / 相机移出 15% margin / mesh 变更落入 footprint;**每帧最多刷新一个远级联**分摊成本;atlas 不清整张、只清待刷象限。
- 采样 = **PCSS**(6 tap blocker search 估半影半径 → 12 tap 旋转 Poisson PCF),`textureGather` + 手动双线性保证跨后端一致;级联过渡带按屏幕抖动随机选级避免接缝;bias = 法线偏移 texel×(1.2+2·slope)。

### 3.4 大气/天空(Hillaire 2020 精简版)

- 三张 LUT:transmittance 256×64 + multiscatter 32×32(**启动一次**);sky-view 192×108×2(日/月,**仅天体角度变 >5e-4 rad 或相机高度变 >1m 才重画**)。
- **Ambient cube 6×1**:6 方向辐照度,所有需要"天空环境光"的 pass(云、水反射、雾、deferred ambient)共享同一来源——**雾色=天空色、反射=天空色,视觉自洽**的统一性是最值得偷的设计。
- 星星(哈希网格点星+银河 fbm)、月盘(环形山 hash)、日盘(临边昏暗)全程序化叠加在 deferred 天空分支。

### 3.5 体积云与光柱

- 噪声 GPU 烘焙一次(128³ Perlin-Worley + 32³ Worley 细节 + 512² 天气图),运行时零噪声计算;**三频 Worley 打包 RGB 三通道**,按距离选通道。
- March:56 步 + IGN jitter;密度>0.002 才进入 6 步向光 march;Wrenninge 多次散射;提前终止 T<0.01。
- **Temporal 是关键**:march 目标再砍半(2×2 块每帧只新算 1 texel,4 帧轮换),其余 texel 用上帧重投影 + 3×3 邻域 min/max 放宽 clamp——**每帧只 raymarch 1/4~1/8 的云像素**。
- 光柱:半 res 14 步视线 march;合成时用 march 长度做**双边 2×2 上采样**(不连续处取最近)。

### 3.6 水:折射 + SSR(本仓库用 SSR,与 threejs-punk 对照见 §5)

- 折射:屏幕偏移 ∝ 法线差,按厚度与距离衰减;**折射采样点比水面还近则回退原 uv**(防翻到前景);厚度 → Beer 吸收 + 群系 tint。
- **SSR 工程细节**:几何级数步进(×1.13,近密远疏)40 步 → 厚度窗口判命中 → 5 次二分 refine → 屏幕边缘/行程双渐隐 → **失败回退程序化天空反射**(不是黑屏不是消失)。
- **glossy SSR(湿地面)采上一帧 TAA 输出**而非本帧——反射自带 TAA 降噪,代价 1 帧延迟。
- 水波迭代次数按距离分档(20/12/7)。

### 3.7 TAA、bloom、曝光、SSAO

- TAA:Halton(2,3) 8 帧 jitter;**3×3 邻域取最近深度像素做重投影**(抗边缘鬼影);YCoCg 方差 clip;**内嵌上采样**(render_scale<1 时无独立放大 pass,历史缓冲建在输出尺寸,按 jitter 样本距离高斯加权)——DLSS-lite。
- Bloom:6 级链;**down 第一级 clamp 到 3000** 防太阳炸 firefly;up 用 pipeline 加法混合直接叠。
- **自动曝光不建独立 mip 链**:采 bloom down 第 1 级(1/4 res,已是优质低通),16×12 网格 log2 亮度 + 中心高斯权重;**不对称适应速度**(变暗快 2.2、变亮慢 1.1,符合人眼);曝光 RT 的 g 通道存平均亮度驱动 **Purkinje 夜视蓝移**(暗场景去饱和偏蓝,一行 shader 换真实夜视)。
- SSAO:半 res 10 样本黄金角螺旋;**无专用降噪 pass**——噪点靠 4 帧轮换的半 res 偏移 + TAA 吞掉,合成时 2×2 双边(深度+法线)上采样。
- **IGN(Interleaved Gradient Noise)全管线共用**:阴影 PCF、SSAO、march jitter、级联选择都用同一个无纹理 hash + 帧序号偏移。

### 3.8 G-buffer 细节

4 RT:albedo(sRGB)/ 法线×2(平滑+几何,oct 编码)/ 光照(sky+block+顶点AO+flags)/ 材质(光滑/金属/SSS/自发光)。手持物单独 pipeline `depth=ALWAYS` 永远在最前且**运动向量强制为 0**(零重投影鬼影)。

### 3.9 性能取舍一览(本案例的预算纪律)

| 项目 | 策略 |
|------|------|
| DPR | 封顶 1.5 |
| 远阴影级联 | 跨帧缓存,每帧至多刷 1 个 |
| Sky-view LUT | 角度/高度超阈值才重画 |
| SSAO / 光柱 | 半 res,4 帧轮换子像素偏移 + TAA 补回 |
| 云 | 1/2 或 1/4 res × temporal 再 ÷4(等效 1/16) |
| TAA | 内嵌上采样,无独立放大 pass |
| 曝光 | 复用 bloom 第 1 级,不建独立 mip 链 |
| 水波 | 迭代数按距离分档 20/12/7 |
| 效果降级 | pipeline 未就绪即关;SSR 依赖 TAA 连带 |

## 4. 程序化内容(零美术资产)

### 4.1 纹理(`wc_textures.c`,1463 行)

- 每种方块 CPU 生成 16×16 **三层同步**:albedo + normal/height + spec(smooth/metal/SSS/emit 四通道打包一张)——材质参数与图案天然对齐(矿脉亮且光滑)。种子 = 方块名字符串 hash,天然确定性。
- 原语:**可平铺** value noise(晶格 mod 周期)/ fBm / Voronoi(环绕周期折返)/ 逐像素白噪声;emboss(高度图对角差分把假凹凸烘进 albedo)。
- 草/叶/水只存**灰度亮度**,真颜色由 shader tint 乘——MC 式生物群系变色;侧面草 alpha 通道复用为"是否 tint"掩码。
- **mipmap 是重头戏(三个独立技巧)**:
  1. **线性空间平均**(避免 mip 变暗发灰);
  2. **alpha bleed**:cutout 纹理把不透明邻居颜色迭代 4 轮填进透明区,防远处黑边;
  3. **覆盖率保持 alpha 缩放**:记录 mip0 的 alpha-test 覆盖率,每级 mip 二分搜索 12 次找缩放系数 k 使覆盖率不变——**树叶远处不变实心也不消失**。这是 alphaTest 植被的必备处理,Three.js 里几乎没人做。

### 4.2 音频(`wc_audio.c`,262 行)

- 万能公式:**白噪声 → Butterworth 带通 → 指数包络**。材质差异只调三参数(中心频率/Q/时长):石 1800Hz、木 900Hz、玻璃 5200Hz、沙 3800Hz;事件差异只调 pitch/gain/时长缩放 + 双层叠加。播放再加 ±15% 随机 pitch。
- 雷声:低通截止 900→90Hz 指数下滑(隆隆滚远),三段包络;雨声:4 秒白噪声塑形 + **等功率交叉淡化**(sqrt t)预制无缝循环体,运行时一阶低通跟随雨强。
- 对应 Web Audio 原生 API(BiquadFilter + exponentialRamp),浏览器端可直接复刻。

### 4.3 粒子/萤火虫/图标

- 粒子 = **小立方体**(非 billboard),每帧 CPU 展开进动态 VBO 画进 G-buffer;碎块 uv 取原方块纹理的随机 3×3 子区——**像从方块上掰下来的**;上限 600,池满丢最旧。
- 萤火虫 = 三轴异频正弦速度目标的一阶跟踪(温和游荡)+ **尺寸按 sin^0.6 脉动**做闪烁(幂 0.6 让亮期占空比更长)——零光源成本。
- 背包图标 = **CPU 软件光栅**:3 面片逆仿射采样 + 4×4 超采样,直接用方块纹理像素生成,不渲 3D 模型。

### 4.4 加载壳(`web/index.html`)

- canvas 常驻、覆盖层只隐藏(否则 swapchain 建成 0×0);wasm 用 `.br` + Content-Encoding 让浏览器原生解码;资产走内容 hash + immutable 缓存;`?profile=mt|st` 强制覆盖线程模式。

### 4.5 画质预设表(`wc_settings.c`)——现成的分级对照

| 参数 | LOW | MEDIUM | HIGH(默认) | ULTRA |
|------|-----|--------|-------|-------|
| render_distance(区块) | 6 | 8 | 12 | 16 |
| render_scale | 0.75 | 0.85 | 1.0 | 1.0 |
| 阴影 | 关 | 1024/64m | 2048/128m | 3072/192m |
| SSAO | 关 | 开 | 开 | 开 |
| 体积雾 | 关 | 关 | 开 | 开 |
| 云 | 快 | 快 | 精致 | 精致 |
| SSR | 关 | 开 | 开 | 开 |

TAA/Bloom 四档恒开——**预设只调"大头"参数,便宜且感知强的常驻**。与 threejs-punk 的设备分级同思路。

## 5. 与 threejs-punk 的对照(两条技术路线的取舍)

| 维度 | threejs-punk(单场景秀技) | WebCraft(系统性世界) |
|------|--------------------------|----------------------|
| SSR | **删掉**,湿地面改平面镜像 RT(整地面 SSR 不值) | **保留**,但只在水面/湿地,且失败回退天空、采上帧 TAA 降噪 |
| 反射哲学 | "暗示"级强度 0.08,不求真 | 折射+SSR 求真,但回退链完整 |
| 预算思路 | 设备分级 + 半 res + frame skip | 画质预设 + 半 res + **temporal 复用**(云 ÷16、阴影缓存) |
| 内容 | 美术资产(GLB/贴图/视频) | **零资产**,全程序化 |
| 世界 | 固定场景,手工摆放 | seed 无限世界,一切确定性生成 |
| 共同纪律 | 预算集中开关、DPR 封顶、单向降级、效果可关 | 同左——**好工程殊途同归** |

**核心启示**:SSR 不是"能用/不能用"的二元问题——threejs-punk 删它是因为整地面全 res 跑不起,WebCraft 留它是因为水面小面积 + 几何步进 + 回退链 + TAA 降噪把成本压进了预算。**判断标准是"成本是否进了预算",不是技术本身。**

## 6. 移植技巧精选(Three.js 落地)

**WebGL2 即可(优先偷)**:
1. **覆盖率保持 mipmap + alpha bleed**——alphaTest 植被远看密度恒定,DataTexture mip 生成时 CPU 二分即可,12 次二分成本可忽略。
2. **半 res pass + 4 帧轮换 2×2 偏移 + 双边上采样**——SSAO/体积光等低通信号信息量 4 帧补回全 res;EffectComposer 半 res RT + frame%4 uniform。
3. **云的 1/4 march + 方向重投影 temporal**——ping-pong RT + march pass + resolve pass,慢变信号通用。
4. **SSR 几何步进 + 厚度窗口 + 二分 refine + 失败回退程序化天空**——标准全屏 ShaderMaterial。
5. **glossy SSR 采上一帧 TAA 输出**——反射免费降噪。
6. **曝光采 bloom 第 1 级 + 不对称适应速度 + Purkinje 夜视**——几乎零成本。
7. **天空 LUT 统一驱动雾/反射/环境光**——视觉自洽的源头;PMREMGenerator 可作平替。
8. **IGN 全局抖动**——一行 GLSL,所有 pass 共用。
9. **u8 直存 + 平行查表 + toroidal chunk 网格**(Uint8Array + Uint16Array slot 池)。
10. **时间预算自适应 job 调度**——滑动平均估算成本,rAF 空闲预算直接照搬,Worker 池 + Atomics 对应 lock-step round。
11. **洞穴粗网格三线性插值**——3D 噪声成本 ÷64。
12. **版本号丢弃过期异步结果**——Worker 乱序完成的通用容错。
13. **程序化音效公式**(白噪声+带通+指数包络)——Web Audio 原生复刻;雨声等功率交叉淡化循环。
14. **指数趋近物理** `v += (target-v)(1-e^(-k·dt))`——帧率无关,比 `lerp(v,t,k·dt)` 更正确。
15. **20 字节/quad vertex pulling**——DataTexture/InstancedMesh + onBeforeCompile 可近似。

**WebGPU-only**:GPU-driven 剔除展开(compute + indirect draw)、textureGather 手动双线性(WebGL2 可退化为 4 次采样)、3D 噪声 compute 烘焙(WebGL2 可 CPU 预生成或多 pass 代替)。

## 7. 源码地图

| 主题 | 文件 |
|------|------|
| 核心数据结构(chunk/section/帧 UBO) | `src/webcraft/wc.h` |
| 游戏循环/流式预算/水 tick | `wc_game.c` |
| chunk 流式/job 调度/版本容错 | `wc_world.c` |
| 地形生成 | `wc_gen.c` |
| 光照洪泛 | `wc_light.c` |
| 网格化/顶点压缩/分桶 | `wc_mesh.c` |
| GPU 网格池/OffsetAllocator | `wc_mesh_store.c` |
| 渲染器主体/pass 序列/级联缓存 | `wc_render.c` |
| 程序化纹理/mip 三技巧 | `wc_textures.c` |
| 程序化音效 | `wc_audio.c` |
| 粒子/萤火虫/手持物 | `wc_entities.c` |
| 画质预设 | `wc_settings.c` |
| 触屏手势状态机 | `wc_touch.c` |
| WASM 加载壳 | `web/index.html` |
| 帧 UBO/IGN/半 res 偏移 | `shaders/wc_frame.glsl` |
| 大气 LUT | `wc_transmittance/multiscatter/skyview/sky/sky_ambient.glsl` |
| 云/天气 | `wc_clouds.glsl, wc_clouds_temporal.glsl, wc_noise_*.glsl` |
| 阴影采样(PCSS) | `wc_lighting.glsl` |
| 水/SSR | `wc_water.glsl, wc_deferred.glsl` |
| TAA/曝光/bloom/final | `wc_taa/exposure/bloom_down/bloom_up/final.glsl` |
