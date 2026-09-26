# 案例:Threejs-Punk — WebGPU + TSL 赛博朋克雨巷(完整萃取)

> 来源:2026-09-26 对 https://github.com/anshul360/threejs-punk 全仓库源码 + 官方文档(README/AGENTS.md/docs/techniques/)萃取。在线 demo:https://threejspunk.vercel.app/
> 作者:Anderson Mancini + Sunag(TSL 作者),TSL Workshop 2026 修订版。**代码 MIT;public/ 下模型/贴图/音视频不在 MIT 内,不可直接搬运。**
> 一句话:**这不是一个"堆效果的 demo",是一个"每个炫技效果都被迫回答了性能问题"的工程范本——学它的预算纪律,比学它的 shader 更值。**

## 0. 什么时候读这份案例

| 场景 | 读哪节 |
|------|--------|
| 任何 Three.js 项目的骨架/目录/启动顺序 | §1 架构 |
| 帧率掉了不知道砍什么 | §2 性能预算(本案例最值钱的部分) |
| 做 GPU 粒子(雨/雪/落叶)且要与几何碰撞 | §3 碰撞雨 |
| 做湿地/水面/镜面反射 | §4 湿地面(含"为什么不用 SSR"的教训) |
| 做物体表面动态效果(水滴/霜/锈迹) | §5 车身雨滴 |
| 写 TSL / 从 GLSL 迁 WebGPU | §7 TSL 模式表 |
| 手机端 WebGL 项目(如 AR 农学) | §8 兼容性警示先读 |

**前置警告**:本仓库是 **WebGPU-first**(`three/webgpu` + TSL,Three r185),AGENTS.md 明令禁止自定义 GLSL。TSL 代码**不能**直接搬进 WebGL 项目;但 §1/§2 的工程模式与 WebGL 完全通用,§3–§5 的思路在 WebGL 里有等价实现(compute → transform feedback 或 CPU 预计算;节点材质 → onBeforeCompile / ShaderMaterial)。

## 1. 架构:factory composition,不是游戏引擎

- **无 ECS、无场景大类**。`src/main.js` 用工厂函数搭一堆普通对象(`world`/`pipeline`/`cameraDirector`/`renderLoop`/`appShell`),显式生命周期,接线全在 main.js。
- **Feature flags 模式**:`world/features.js` 集中开关;被关掉的 feature **返回 `null`**,渲染循环全程可选链 `world.rain?.update(...)`。新功能照此办理,不要写 if 分支进循环体。
- **启动顺序**(乱一步就出黑屏/卡顿,照抄):
  1. 设备预算(`applyDevicePerformanceDefaults`)——**在创建 renderer 之前**
  2. 核心:camera → scene+sun → renderer
  3. 世界:GLTF 并行加载
  4. 灯光/环境:HDR env
  5. 后处理管线(+ localStorage 里的 look 预设)
  6. 运行时:adaptive DPR(intro 之后才启用)、相机导演、UI 壳、音频
  7. **Warmup:拆分 shader 编译**(见 §2)——Safari 必须编译完才准进循环
  8. 渲染循环启动,intro 异步叠加其上
- **一帧的顺序**(createRenderLoop.js,顺序即正确性):
  相机导演 update → 碰撞高度 RT 更新 → 雨 compute → 天空/地面/车体等世界系统 → (可选)地面反射 RT → 后处理同步相机 + DoF 焦点 → `post.render()` → FPS 采样(adaptive DPR)。
- **STRIP 纪律**(STRIP.md):场景可逐层剥皮到最小核 `bootstrap + scene + city + ground + post + walk/orbit + loop`。剥皮顺序:intro → chromeUi → walkUi → audio → smoke → planes → rain → sky → car → ground → city。**做教学 fork 或排障时按此顺序关,一次关一层。**

## 2. 性能预算:为什么这个场景又快又好看

> 原话:"Most AI-generated Three.js demos stack heavy effects until the GPU chokes." 所有杠杆都是**显式写在代码里的开关**,集中在 `platform/performanceProfile.js`。

| 杠杆 | 做法 | 数值 |
|------|------|------|
| 半分辨率 pass | GTAO / bloom / lensflare / 地面反射 RT 全部降采样 | `*ResolutionScale: 0.5` |
| Frame skip | 碰撞高度图、地面反射不必每帧更新 | `*FrameSkip: 1`(每 2 帧 1 次) |
| 距离衰减 | 车身雨滴强度 20m→32m 渐隐到 0;视频广告牌 CPU 距离剔除 play/pause | fadeStart 20 / fadeEnd 32 |
| 渲染分层 | 雨在 layer 2、烟在 layer 3,**GTAO 预 pass 关掉这些层**(粒子会破坏 AO 法线) | `RAIN_LAYER = 2` |
| 拆分编译 | 关键路径(城市/地面/beauty)先编译,雨/烟/飞机延到 intro 期间编译 | `warmup.js` |
| 设备分级 | 手机:lensflare/广告牌/GTAO 全关;Safari/苹果移动端:DPR 上限 1.25、关 adaptive DPR、DoF 全平台默认关 | `applyDevicePerformanceDefaults` |
| DPR 上限 | `maxPixelRatio: 1.5`(桌面)/1.25(苹果移动端) | `getStaticPixelRatio()` |
| Adaptive DPR | **单向降级**:FPS 连续 2 个窗口 < 50 → 降到 0.85 且**永不回升**(回升会抖,只有刷新页面才重置) | `adaptiveDpr.js` |

**两条血泪教训(比技巧重要)**:
1. **SSR 被删了**(commit `ea84fd7`)。湿地面改用"手动镜像相机 + 半 res RT + 按粗糙度混 emissive"。屏幕空间反射在预算内跑不稳,砍。"看起来反光"≠"真的 SSR"。
2. **每帧每个雨滴 CPU raycast 被删了**(commit `89e766f`)。改成"高度贴图 + GPU compute"。凡是"每对象每帧 CPU 查询"的写法,都是未来的性能债。

**dev 工具**:`window.__app.perf` 运行时 A/B 每个开关;Three.js inspector 走设置里的 Development Mode。给性能开关留运行时入口,是调试帧率的前提。

## 3. 碰撞雨:高度贴图 + GPU compute(招牌技巧)

**问题**:5000 个雨滴要落在屋顶/车/地面上,不能穿模,不能 CPU raycast。

**核心思想**:把碰撞从 3D 射线问题降维成 **2D 高度场**——一张从头顶正交相机渲出来的 RT,每个 texel 存该柱体最高表面的 **world Y**。

**步骤**:
1. **高度 pass**(`createCollisionHeight.js`):正交相机从 y=50 垂直向下,视锥 100×100 世界单位,**中心每帧跟随玩家相机 XZ**;RT 512²、HalfFloat、**nearest 过滤、无 mipmap**(双线性会在边缘混出"平均高度",雨就悬空了)。`scene.overrideMaterial` 输出 `vec4(positionWorld, 1)`。
2. **隐藏名单**(`collisionHideObjects.js`,最容易踩的坑):渲高度图时必须 `visible=false` 掉——雨本身(否则雨丝变"地面")、天空穹顶(否则封顶)、烟、飞机。**新增任何大型透明层/粒子系统,都要加进这个名单。**
3. **Compute 模拟**(`createCollisionRain.js`):
   - `instancedArray` 存位置/速度,`renderer.compute()` 更新,默认 5000 实例(clamp 500–5000)。
   - 雨区是相机前方 15 单位、60×60 的盒子(高度图 100×100,略大一圈防边缘穿帮);XZ 用 `fract` **环形回绕**,相机移动不用重新分配。
   - 每滴:积分位置 → `getUV(xz)` 采样高度 → `if (y < floorY + 0.05)` GPU 分支重生到 y∈[20,35]。**`getUV` 必须与写 RT 的 pass 用同一个函数**,不一致就是雨穿屋顶的第一嫌疑。
   - 水花:同一张高度图定 Y(+0.06),5 帧横排图集动画;贴图没有真 alpha,**不透明度取 `.r` 通道**。
4. **绘制**:雨丝和水花各一个 instanced PlaneGeometry,`billboarding()` 朝相机;`depthWrite:false, transparent:true, toneMapped:false`;**`frustumCulled=false`**(实例活在 world space,包围球算不准,错误剔除比全画更糟)。
5. **预算旋钮**:`collisionRainResolution: 512 / collisionRainFrameSkip: 1 / collisionRainCount: 5000`,全在 performanceProfile。

**排障口诀**:雨穿屋顶→查隐藏名单、查 nearest 过滤、查高度 pass 是否在 compute 之前;边缘突兀→高度体积和雨区一起放大。

**移植检查单**:正交顶视相机+RT(half-float,nearest)→ override 材质输出 world 位置 → 体积跟随相机 XZ → 隐藏名单 → pass/compute 共享 getUV → compute 积分+采样+GPU 重生 → instanced billboard 绘制 → 更新顺序 **height → compute → 主渲染** → 分辨率/数量/跳帧做成配置。

## 4. 湿地面:涟漪法线 + 手动平面反射(不用 SSR)

两套系统别混淆:**地面 = 涟漪 + 反射;车身 = 程序化水滴(§5)。**

**涟漪**(`tsl/rainRipples.js`):
- 固定 **5×5 邻域**(25 cell)循环,每 cell 哈希中心 + 相位 `fract(0.3t + hash)`,环距离 `d = length(v) - (MAX_RADIUS+1)·t`,用中心差分(h=0.001)近似正弦环导数,累加成法线 `vec3(xy, sqrt(1-dot(xy,xy)))`。
- **用 world XZ 采样,不用 mesh UV**——大平面上环不漂移、贴图重复处无接缝。这是所有"地面型程序纹理"的通用原则。
- 成本是**固定的** 25 cell/像素,与雨滴数量无关。
- 两路输出:法线强度 0.015 混进 normalNode;反射扰动 0.08 混进反射 UV(水面扭曲镜像)。

**平面反射**(`createGround.js#updateReflection`):
- 独立 `renderer.render` 进自己的 RT,**不要把镜像 pass 折回 TSL `PassNode` 图里**——WebGPU 下反射纹理会同时是采样纹理和渲染附件,冲突。内置 `reflector()` 同理回避。
- 镜像相机:视点/目标点对地面求镜像,拷 FOV/aspect/near/far;**斜裁剪平面**(Lengyel 式)裁掉地面以下几何,WebGPU 与 WebGL 的 `projectionMatrix.elements[10]` 写法不同,按 `renderer.coordinateSystem` 分支。
- 镜像相机**关掉 RAIN_LAYER**(雨丝不能被反射成实体);渲前藏地面自身,渲后恢复。
- **反射不写 envMap,写 emissive**:`reflection.rgb × (1-roughness) × uReflectionStrength(0.08)`。粗糙度越低越反光——水洼处自然捡起霓虹。强度 0.08 是"暗示",不是铬地板。
- 半 res(`0.5`)+ frame skip(1)。

**湿 PBR 三件套**:albedo/roughness/normal 同一 UV 平铺(repeat ~14.9),`roughnessNode = roughness.r × 0.55`,metalness=0。

## 5. 车身雨滴:程序化水滴图(无模拟纹理)

改自 [rocksdanister/rain](https://github.com/rocksdanister/rain)(BigWings 风格 MovingDropLayer)——**移植必须保留这个 credit**。

- **纯数学图**:网格哈希 + 下落水滴 + 拖尾 + 卫星小滴,返回 `vec2(mask, edge)`。无 RT、无逐 texel 模拟,`update(delta)` 只推进 uTime。
- **有限差分法线**:mask 求 3 次值(中心、+εx、+εy,ε=0.005),`normalOffset = (cx-c, cy-c)` 得切空间偏移——**"标量 mask → 法线"的通用套路**,任何凸起类程序纹理都能用。
- **UV 分通道**:PBR 贴图走 UV0,雨走 **UV1**(`TEXCOORD_1`)。UV1 在 Blender 里单独展开过(要湿的面);**不要复用镜像/重叠的 UV0**,否则水滴跨无关 island 平铺。
- **静态水珠层在车上被禁**(`getCarRainLayerWeights` 强制 static 权重 0)——UV1 上会闪烁。只留移动层。
- 材质接线:paint → MeshStandardNodeMaterial;玻璃 → MeshPhysicalNodeMaterial(低粗糙度、clearcoat 1、**不透明**而非 alpha 混合)。`roughnessNode = mix(base, wet, mask×uIntensity)`,normalNode 叠加偏移。
- **一个 uniform block 全材质共享**(uTime/uIntensity/uScale/uDropSize/…),不要每个材质各建一套。
- 距离衰减见 §2。

## 6. 其余子系统(各一句话)

- **Intro 雨玻**:车身雨滴同一族图,应用到**宽高比修正的屏幕 UV** + 折射偏移 + 降采样模糊;intro 期间 DoF/lensflare 调弱(玻璃本身已模糊);intro 结束即 dispose。
- **后处理栈顺序**(`postprocessing.js`):GTAO 预 pass(法线 MRT,关雨/烟层)→ 主 pass **MRT 出 color+emissive**(emissive 驱动 bloom)→ 半 res bloom → (可选)lensflare → DoF(可分离 boxBlur,按视深对焦点混合;Safari 关)→ cyberpunk 调色(双雾:几何雾+天空雾、对比/饱和、**边缘色差**、暗角、胶片颗粒)→ SMAA。
- **Look 预设**:`neutral/neonNoir(默认)/magentaRain/tealDusk/silentHill/sinCity`,各调 bloom/调色/色差/暗角/颗粒,存 localStorage——**"预设 = 一组参数表"是低成本高感知的增值做法**。
- **天空**:内翻球 + 预烘焙噪声贴图的程序云,穹顶跟随相机 XZ,太阳染色。
- **视频广告牌**:视频采样 × 径向暗角,走 `emissiveNode` 喂 bloom MRT;CPU 距离剔除暂停解码。
- **烟**:instanced sprite,layer 3 排除出 GTAO。
- **行走**:`three-mesh-bvh` 对城市+碰撞体+车建 BVH;pointer-lock 移动、台阶处理、冲刺 FOV、蹲伏;移动端虚拟摇杆。
- **DoF 焦点**:GSAP 平滑的焦点对象,orbit 模式点击对焦、walk 模式视线射线更新。

## 7. TSL 模式表(写 WebGPU/TSL 时对照)

| 模式 | 用途 |
|------|------|
| `Fn(() => …)()` | 一切可复用子图(水滴层、雾、对比度、涟漪循环) |
| `uniform()` + needsUpdate | CPU 驱动参数(look、雨强、intro 玻璃) |
| `texture(rt, uv)` in compute | 碰撞高度采样 |
| `.compute(count)` + `renderer.compute()` | 粒子更新 |
| `billboarding({ position })` | instanced 雨/水花面片 |
| `If(cond, () => …)` in compute | GPU 侧重生,不回读 |
| `Loop` | 涟漪邻域、可分离模糊 taps |
| 自定义 `TempNode` | 边缘色差 |
| 材质节点槽覆盖 | `colorNode/roughnessNode/normalNode/emissiveNode/opacityNode/vertexNode/outputNode` 代替 ShaderMaterial 字符串 |
| `RenderPipeline` + `post.outputNode` | beauty+调色单图;look/性能/intro 变化时重建 |

导入:`three/webgpu`、`three/tsl`,显示节点在 `three/addons/tsl/display/`。

## 8. 兼容性警示(WebGL/移动端项目必读)

- WebGPU 需要 **secure context**(dev 用 `@vitejs/plugin-basic-ssl`);Safari 的 WebGPU 在"resize + 并发编译 + 多 pass"下会冻,所以该仓库对 Safari 单独降预算、且编译完成才进循环。
- **AR 农学及同类手机 WebGL 项目**:以上 §3–§5 的思路可用,实现必须改写——compute shader → transform feedback/WebGL2 或降格为 CPU 低频更新;节点材质 → ShaderMaterial/onBeforeCompile;平面反射可用 `Reflector`(WebGL 下没有附件冲突问题)。**预算纪律(§2)原样照抄,与渲染后端无关。**
- 资产管线通用:GLTFLoader + DRACOLoader + KTX2Loader(`detectSupport(renderer)`)单例,Draco/Basis transcoder 随产物本地化。

## 9. 源码地图(回仓库查原文用)

| 主题 | 文件 | 入口 |
|------|------|------|
| 应用接线 | `src/main.js` | `init` |
| 渲染循环 | `src/runtime/createRenderLoop.js` | `createRenderLoop` |
| 性能旋钮 | `src/platform/performanceProfile.js` | `performanceProfile`, `applyDevicePerformanceDefaults` |
| Adaptive DPR | `src/platform/adaptiveDpr.js` | `createAdaptiveDprController` |
| 拆分编译 warmup | `src/runtime/warmup.js` | `finalizeStartupLighting`, `compileDeferredStartup` |
| 碰撞高度 RT | `src/world/weather/createCollisionHeight.js` | `createCollisionHeight` |
| GPU 雨+水花 | `src/world/weather/createCollisionRain.js` | `createCollisionRain` |
| 高度 pass 隐藏名单 | `src/world/weather/collisionHideObjects.js` | `collectCollisionHideObjects` |
| 湿地面+反射 | `src/world/ground/createGround.js` | `createGround`, `updateReflection` |
| 涟漪 TSL | `src/tsl/rainRipples.js` | `createRainRipples` |
| 车身水滴 TSL | `src/tsl/surfaceRain.js` | `evaluateCarSurfaceRain` |
| 后处理栈 | `src/post/postprocessing.js` | `createPostProcessing` |
| Look 预设 | `src/post/look/cyberpunkLook.js` | `createCyberpunkLook`, `LOOK_PRESETS` |
| 行走+BVH | `src/controls/createWalkControls.js`, `src/world/bvh.js` | `createWalkControls`, `buildModelBvh` |
| 剥皮指南 | `STRIP.md` | — |
| Feature flags | `src/world/features.js` | `FEATURES` |
| GLTF+Draco+KTX2 | `src/world/loaders/createGltfLoaders.js` | `getGltfLoader` |
