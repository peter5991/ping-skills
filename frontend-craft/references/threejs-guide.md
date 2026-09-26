# Three.js 使用规范(通用)

> 定位:T2 级手法的总指南。做 3D 前先过 `techniques.md` 的分级判断——**WebGL 是最后手段,不是起点**;确认非 3D 不可(可交互模型、空间叙事、产品拆解、AR)再按本文执行。
> 案例库见 `threejs-cases/_index.md`;典范萃取:`threejs-cases/threejs-punk.md`(架构与性能预算)、`case-autopiano-3d.md`(可交互 3D 物件)。

## 0. 三条总红线(与本 skill 全局红线叠加)

1. **3D 不豁免静帧原则**:loading 态/降级态必须先设计好;WebGL 上下文创建失败时页面仍可读(显示静态图 + 说明)。
2. **本地化不豁免**:three 本体、Draco/Basis transcoder、模型、HDRI 全部随产物走,断网双击可跑。版本登记进 `libs.md`。
3. **DOM 层与 WebGL 层各司其职**:UI 动效(HUD、提示、转场)仍只用 `transform`/`opacity`;canvas 内部不受此限,但持续动画必须帧率无关(乘 dt)。

## 1. 渲染器选型:先定后端,再写代码

| 场景 | 选型 |
|------|------|
| 移动端 / 默认浏览器 / 微信 webview 风险 / 教学课件 | **WebGLRenderer**(WebGL2)。兼容性第一 |
| 桌面展示页、可控环境、需要 compute shader | WebGPURenderer + TSL(Three r165+),**必须做 WebGL 回退** |
| 只要展示一个 glTF 模型 | `<model-viewer>`,不引 three |

- WebGPU 需要 secure context(HTTPS 或 localhost);Safari 的 WebGPU 在多 pass + resize 下不稳,选它就要按设备降预算(见 §5)。
- **DPR 上限**:`renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5))`;苹果移动端压到 1.25。不设上限是移动端卡顿第一元凶。

## 2. 应用骨架:factory composition

- 工厂函数 + 普通对象,在 `main.js` 显式接线;不引入 ECS/场景大类。启动顺序固定:**设备预算 → renderer/camera/scene → 资产加载 → 灯光/环境 → 后处理 → 运行时(相机控制/UI/音频) → warmup → 循环**。
- **Feature flags**:可选子系统集中开关,关闭时返回 `null`,渲染循环全程可选链。好处:排障时逐层关闭快速定位,教学 fork 直接剥皮。
- **渲染循环**:一律 `renderer.setAnimationLoop`(它正确处理 XR 与 tab 隐藏),不用手写 rAF。每帧顺序:**相机/输入 → 模拟更新 → 预 pass(阴影/反射/RT)→ 主渲染 → 后处理 → 性能采样**。
- **帧率无关**:`delta = clock.getDelta()`,所有速度乘 delta;插值用 `lerp(current, target, 1 - Math.exp(-k * delta))` 形式,不写死 0.1(高刷屏手感会不一样)。

## 3. 资产管线

- **模型**:glTF/GLB 唯一格式。压缩链:`GLTFLoader` + `DRACOLoader`(几何)+ `KTX2Loader`(贴图,`ktx2Loader.detectSupport(renderer)` 必须调)。transcoder 文件放本地 `/libs/`,loader 单例共享。
- **并行加载 + 进度**:LoadingManager 驱动 loading UI;首屏只加载关键路径模型,次要资产延后(参考 threejs-punk 的拆分编译:关键材质先编译,装饰系统延到 intro 期间)。
- **纹理**:sRGB 只给颜色贴图(`texture.colorSpace = SRGBColorSpace`),法线/粗糙度/金属度保持线性;2 的幂尺寸;能 KTX2 不 PNG。
- **音频/视频**:视频贴图注意解码成本——离屏或远距离暂停播放。

## 4. 相机、交互、拾取

- 展示用 OrbitControls(开 `enableDamping`,update 进循环);第一人称用 pointer-lock + 碰撞(网格碰撞用 `three-mesh-bvh`,不要逐三角形射线)。
- **拾取**:Raycaster 只对有交互的对象求交(白名单),不扫整场景;移动端 touch 与 mouse 统一走 pointer events。
- 多相机模式(orbit/walk/固定机位)做成"相机导演"切换,DOF 焦点等跟随逻辑挂在导演上,不散落在各处。

## 5. 性能预算(核心章,照抄 threejs-punk 的纪律)

**原则:每个昂贵效果要么上 GPU、要么降分辨率、要么砍掉——三者选一并写成开关。**

1. **集中开关表**:一个 `performanceProfile` 对象管所有预算(分辨率缩放、frame skip、实例数、pass 开关),启动时按设备改默认值,dev 环境留运行时 A/B 入口。
2. **半分辨率**:AO/bloom/反射等中间 pass 一律 0.5 倍 RT。
3. **Frame skip**:变化慢的 RT(反射、高度图、阴影)每 N 帧更新一次。
4. **距离衰减/剔除**:细节效果(表面程序纹理、粒子密度)按相机距离渐隐;离屏对象暂停更新。
5. **渲染分层**:`object.layers` 把粒子/特效分出独立层,AO/反射等预 pass 的相机**关掉这些层**——粒子进 AO 会污染法线。
6. **Adaptive DPR 只做单向降级**:FPS 连续数个窗口低于目标 → 降 DPR 且**不回升**(回升抖动比模糊更难受)。
7. **设备分级**:移动端默认关 AA 后处理(用 DPR 换)、关非必要 pass;DoF 类全屏效果默认关,由用户/inspector 开。
8. **instanced 粒子**:`InstancedMesh`/instanced 属性一次 draw call;`frustumCulled = false`(world-space 实例算不准包围球);透明粒子 `depthWrite:false`。

**经典反面教材**(都来自真实项目):逐对象逐帧 CPU raycast → 改高度场/数据纹理;SSR → 平面镜像 RT;全分辨率全 pass → 半 res + 设备分级。

## 6. 材质与着色

- 简单定制优先 `onBeforeCompile` 或节点槽;WebGL 项目写 GLSL 注意:精度声明、`#ifdef` 分支、避免动态循环上限(低端 GPU 编译慢/失败)。
- **"标量 mask → 法线"套路**:程序纹理(水滴/涟漪/霜)输出灰度 mask,有限差分(中心±ε 三次采样)得切空间法线偏移,叠进 normalMap;粗糙度同步往"湿"值 mix。一套解决所有"表面动态细节"。
- **地面型程序纹理用 world XZ 采样**,不用 mesh UV——无接缝、不漂移。
- 反射类效果:**写 emissive × (1 - roughness)**,不迷信 envMap/SSR;强度克制(0.08 量级是"暗示",不是镜子)。

## 7. 后处理

- 顺序纪律:**AO → 主 pass(MRT 出 color + emissive)→ bloom(吃 emissive 通道)→ 景深 → 调色(对比/饱和/色差/暗角/颗粒)→ AA**。
- 调色做成**预设参数表**(`LOOK_PRESETS` 式),存 localStorage;低成本高感知。
- 每加一个 pass,先问:能不能半 res?能不能 frame skip?移动端关不关?——答不出就不加。

## 8. 验收追加项(叠加在 skill 总验收清单上)

- [ ] WebGL context 创建失败有降级画面;`webglcontextlost` 有处理。
- [ ] DPR 有上限;resize 时 renderer 尺寸同步重设。
- [ ] 6x CPU 降速 + 中端手机实机:帧率稳、无 shader 编译长卡顿(warmup 拆分)。
- [ ] 性能开关集中且可运行时切换;无逐帧 CPU 重查询(raycast/矩阵遍历)。
- [ ] 模型/贴图/HDRI 全部本地化且压缩(Draco/KTX2),总量对目标网络可接受。
- [ ] 持续动画全部乘 delta;tab 切走再回来不跳变。
