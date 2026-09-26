# 案例集:iamtechartist — 17 个 Three.js 案例与"AI 如何实现"工作流还原(完整萃取)

> 来源:2026-09-26 对 https://github.com/iamtechartist 全部 17 个案例仓库逐行精读(4 个并行子代理分组:水体 4 / 场景 4 / 机械教育 4 / 实验 5+1)。demo 均在 `https://iamtechartist.github.io/<仓库名>/`。
> 一句话:**这个作者是"AI 对话式开发 Three.js"的完整标本——git 里只有一次上传,迭代全在 AI 对话里;demo 代码里留满了给 AI 读的遥测接口和自验收断言。学他的工作流比学他的 shader 更有价值。**

## 0. 怎么用这份文档

| 目的 | 读哪节 |
|------|--------|
| 学"怎么用 AI 做出这种成品"(核心) | §1 工作流还原 |
| 快速查某个案例怎么实现的 | §3 案例速查表 |
| 找可偷的具体技巧 | §4 移植技巧精选 |
| 给 AR 农学项目用 | §5 对教学项目的借鉴 |

## 1. AI 工作流还原(本文档的核心)

### 1.1 证据链:为什么说全部 AI 生成

1. **git 地层学**:17 个仓库无一例外只有 3-5 个 commit:"Initial commit"→"Add files via upload"→"Create README.md"。**一次性整包上传,零迭代历史**——迭代发生在 AI 对话里,不进 git。Conceptual-X-16 和 geometry-in-flux 多的一次 commit 也只是 README 更新。
2. **README 集体沉默**:17 个 README 全部 1-3 行(一句诗性描述 + Pages 链接),**只有 2 个提到 AI**(spider-robot 和 Aquatic 声明模型来自 Meshy AI;Aquatic 另自曝 "GPT-5.6 Sol animated it")。
3. **代码指纹**:零 emoji、零 meta generator、零 section banner;注释要么为零(单文件仓库),要么只解释"为什么不做某事";无障碍(aria 全套)、reduced-motion、错误兜底面板**恒定超标**——不是人类 demo 作者的优先级,是 AI"一次给全"的输出习惯。
4. **版本同代际**:全部 Three r185/0.185.0 一带(仅 eiffel 0.173、citadel 0.174、3D-Webpage 0.183),同一时期同一 AI 的版本推荐。
5. **命名学**:仓库名 ≠ 作品名,title 统一"代号 — 副题"(Aether Bloom / Lumen Lattice / Volt District / IRIS / AX-4);loading 文案是叙事动词("Forming the shoreline"/"Entering the spring"/"Opening cove")。

### 1.2 工作流六条(按价值排序)

**① demo 自带"AI 可读接口"——最重要的发现。**
每个 demo 都把内部状态暴露给自动化读取:
- 命名全局遥测对象:`window.saltreach`(coastal)/`window.pelagic`(ocean)/`window.tideglass`/`window.yamaai`/`window.__IRIS_DEBUG__`——内含 p95 帧时、drawCalls、场景内部句柄。
- DOM dataset 探针:geometry-in-flux 往 `canvas.dataset` 写 19 项状态;mountain-railway 写 fps/gpuMs 到 `<html>` 属性,注释明言 "Diagnostics are available on <html> without a scene UI"。
- **URL 参数即 API**:tideglass 的 `?at/?view/?night/?tide/?pause`——"发个链接就是我说的状态",AI 对话里复现问题零成本。
- **WebMCP 工具注册**(最前沿):coastal 的 `agent-tools.js` 和 X-16 的 `webmcp.js` 通过 `document.modelContext.registerTool` 把 demo 注册成浏览器内 AI agent 可调用的工具(读状态/切视角/暂停/测性能),带 inputSchema 和范围校验。
> **迁移**:你做 AI 辅助开发时,让 AI 给 demo 留这三样:window 遥测全局、URL 参数定状态、dataset 写关键指标。这是"AI 对话迭代"的反馈回路,没有它 AI 只能盲改。

**② 验收被代码化——"AI 不留解释,留可执行断言"。**
- mountain-railway 的 `scripts/verify.mjs`:Node 无头验证——实例化整个场景,断言 201 个 mesh 顶点全部 finite、36 条 Raycaster 隧道净空射线、6 个道具落地高度 ±0.01m、15000 帧列车模拟 ≥3 次停站,输出一行 JSON。
- astronomers-citadel 的 `body.dataset` 自检协议:门洞对齐误差、桥面净宽、连通图序列化进 DOM——验收 = `document.body.dataset.architectureFaults==='0'`。
- eiffel 初始化末尾跑拓扑自检 + `__PARIS_INIT_ERROR__` 全局错误钩子;X-16/spider-robot 把 fps/drawCalls 写 dataset。
> **迁移**:让 AI 为每个 demo/课件写一次性断言脚本(或页面内自检),"改完跑 verify"代替肉眼回归。与本 skill `references/verification.md` 的数值神谕完全同构——这个作者就是把 oracle 当开发基础设施用。

**③ 双实现镜像:CPU 与 GPU 写同一份函数。**
四水体仓库共享的套路:地形/波面函数在 JS 和 TSL/GLSL 各写一份(coastal coast.js、tideglass core.js 一份系数喂 CPU 碰撞+GPU 位移),甚至 JS/WASM 同构求解器(coastal 用 AssemblyScript 抄一遍浅水求解器编译成 3.8KB wasm,零拷贝调 kernel,失败静默回退 JS)。geometry-in-flux 的 morph 公式 GPU 变形 + JS 拾取双写,零回读精确 hover。
> 这是 AI 最擅长的事:"把这段函数翻译成 TSL/WASM/GLSL 并保持数值一致"——机械但易错,人类只需验证两处行为一致。

**④ 否定式注释 = 调试史的化石。**
高频注释模式是解释为什么放弃某方案:"its former wet-sand BRDF made the entire shelf look gelatinous"(ocean)、"Testing any positive elevation made every passing half-wave whiten the shelf"。每条对应一轮"出 bug→诊断→改方案"。无 TODO、无半截功能——**每轮对话收敛到可发布态才停**。

**⑤ 内容全部数据表驱动。**
教学/图鉴文案一律做成同构 JSON 表:X-16 的 tour 数组/descriptions 字典、Cell 的 CELL_INFO + ANNOTATIONS、Atlas 的 ATLAS_COLLECTION、Chronograph 的事件名串。**代码与内容分离,AI 迭代时只改 JSON**——这正是 AR 农学"讲解模块 = 时间轴 JSON"架构的同构验证。
模块划分同理:mountain-railway 按**场景学科**分文件(geology/architecture/vegetation/cinematography/luminous)而非软件分层——AI 按"让这个场景可信需要哪些学科"切分。

**⑥ 工程完备性恒定超标 + 模板复用。**
全部 17 仓有:WebGPU→WebGL2 回退(或显式 WebGL 选择)、pixelRatio cap、delta clamp、visibilitychange 暂停、错误面板 + 重试、aria 全套、prefers-reduced-motion、ACES toneMapping、LCG/mulberry32 同常数种子。四水体仓共享同一套 `$` 选择器、U uniform 集线器、PRNG 常数(374761393/0x6D2B79F5)——**提示词/项目约定模板在跨项目复用**。
> **迁移**:沉淀一份你自己的"项目宪法"(技术栈版本、目录约定、遥测接口、验收脚本模板),每个新项目喂给 AI——这是这个作者 17 仓一致性的来源。

### 1.3 人机分工与技术栈演进

- **资产**:Meshy AI 出模型(spider-robot 的 GLB、Aquatic 的 22MB 鱼)、外部 FBX(sun-temple 的行走/挥手)→ **AI 写程序化动画接管资产**:Aquatic 给无动画鱼写 9 节骨链游动(头反向补偿 -0.88),spider-robot 对自动绑骨模型做运行时 CCD IK + 对角步态。**"AI 资产 + AI 程序化驱动"的双层管线**,不买动画资产。
- **演进轨迹**:ocean(WebGL2 GLSL 单文件,CDN)→ coastal/tideglass(WebGPU TSL,多文件,vendor 本地化,worker/WASM/批合并工程化陡增)→ Aquatic/Chronograph/Circuit(引入 Vite 构建,**源码不入库,只传产物**)。AI 辅助深度递增:从"AI 写 shader"到"AI 写求解器+编译管线+agent 工具"。
- **诚实声明话术**:教育类仓库自带免责("interpretive mechanism, not a reconstruction"、"stylised scientific visualisation, not clinically validated")——AI 生成教学内容的标配,你的课件 About 页也该有。

## 2. 跨仓库同构指纹总表

| 维度 | 指纹 |
|------|------|
| HTML 骨架 | viewport-fit=cover + 大段内联 style + fixed 全屏 canvas + importmap + module script |
| Three 引入 | 单文件仓→jsdelivr/esm.sh CDN;多文件仓→本地 vendor r185 + 运行期 `REVISION!=='185'` throw 校验 |
| 渲染后端 | WebGPU+TSL(新)/ WebGL2(旧),必有回退路径 |
| 遥测 | window.X 全局 / dataset 探针 / URL 参数 / WebMCP 工具,至少占一样 |
| 氛围系统 | **单标量驱动**:nightMix(eiffel)/transformation.value(sun-temple)/modes 表 lerp(mountain)/电压档(Circuit)——一个连续标量 fan-out 到所有材质光源,过渡天然平滑 |
| mesh 命名 | 叙事化('Rising monumental sun disc'/'Cathedral of Totality')——服务调试和 AI 遍历场景树 |
| UI | 玻璃拟态面板 + `--fill` 渐变滑条 + 全大写微排版 + 几何符号图标(☀◒☂☾) |
| 性能 | pixelRatio cap、delta clamp、frustumCulled=false(粒子)、tab 隐藏暂停、自适应降画质闭环(EMA 帧时→降 DPR/质量,滞回防振荡) |
| 动画 driver | 解析运动学/程序化为主,几乎零关键帧 |

## 3. 案例实现方式速查(17 个)

### 水体(4)
- **coastal-simulation** ⭐工程最完整:有限体积浅水求解器(交错网格+正性限制器,241×401 网格),**JS/WASM 同构双实现**(AssemblyScript,3.8KB wasm 零拷贝),Web Worker 物理线程 30Hz 发包 + 渲染侧时间插值,**烘好初始状态快照秒开**(失败本地复算兜底),WebMCP 5 工具。WebGPU/TSL + vendor r185。
- **ocean-simulation**:GPU FFT 三级联 JONSWAP(1792/211/27.3m 波长域),**近岸用程函方程旅行时场校正 FFT 相位**(绕角折射/岬角遮蔽一次预解),折射光线面积投影焦散,足迹带限解析微表面防远处高光闪烁,EMA 自适应质量闭环。单文件 2314 行,WebGL2。
- **tideglass-cove**:无求解器解析水面,**JS/TSL 双写镜像**(CPU 拾取与 GPU 位移永远一致),带深度合法性校验的折射 RT + 水柱路径 Beer 吸收,微缩"海水切片"侧壁(顶点水位权重),海豚=单调三次样条放样,按材质 uuid 批合并静态网格。WebGPU/TSL。
- **Threejs-Aquatic-Simulation**:Meshy AI 22MB 无动画鱼 GLB + **程序化骨链游动**(9 节 bend/pitch 四元数相位递推 + 头反向 -0.88 + pitchCurvature)。Vite 构建产物(源码未入库),`window.__THREE__` 残留=构建后未人工 review。

### 场景(4)
- **mountain-railway-diorama** ⭐最成熟:15 个领域模块 + verify.mjs 无头验收;世界锚定一条 CatmullRom 闭环曲线(车站/隧道/镜头全部反查 u 参数);**镜头调度器**(11 机位按列车进度切换,过渡路径采样 32 点算地形避障抬升);四氛围模式 = 20 字段参数表 + `1-exp(-dt·1.5)` 全场景 lerp;GPU 计时滞回自适应 DPR;手写 1/4 分辨率 bloom。
- **eiffel-tower-district**:**真实 OSM 数据**(Overpass API,10083 元素)内嵌 + 切平面投影 + RDP 分级简化 + `building:levels×3.15m` 高度启发式,连 ODbL 署名都处理了;铁塔按结构尺度分 heavy/medium/fine 桶,**fine 桶整桶按距离裁剪**(LOD 不降模而删细节层);nightMix 单标量驱动昼夜;阴影烘焙一次后冻结。
- **sun-temple**:16.7MB 单文件(FBX base64 内嵌 + `FBXLoader.parse` 绕网络);**单标量编舞** transformation.value + heavySegment 错峰切五个子动画,末端 sin 衰减回弹做巨石"重量感";TSL 程序化砂石族(一个节点函数 × 六组参数,positionWorld 驱动免 UV 免贴图);女祭司状态机(走出→挥手→转身→走回)双 action 交叉淡入。
- **astronomers-citadel**:932 行哥特建筑 builder 三分件(教堂/天文台/桥,自包含可组合);Canvas 2D 程序砖贴图;**body.dataset 自检协议**(结构 fault 全序列化)。

### 机械/教育(4)
- **Conceptual-X-16** ⭐教学范式:**整机 = solve(theta) 纯函数**(滑块曲柄闭式解,720° 映射四冲程,点火顺序从上止点自动推导),爆炸视图是与 theta 正交的第二标量;声明式五步 tour({title,text,camera,mode,rpm,duration});Ghost/Section/Isolate 三态(单 clipping plane + focusWeight 透明度 + damp);WebMCP 工具注册;PMREM 摄影棚(5 块自发光板)。
- **Chronograph** ⭐慢动作解剖:**固定步长积分器(1/240s)+ 状态历史环形缓冲**——慢放/单步/拖 scrub/倒带统一为"改 accumulator 乘子 + 移 cursor",回放中操作会 branch 新历史;**解析擒纵 + 事件命名字幕**(Unlock/Impulse/Release/Locked,0.01× 下逐拍正确);齿数表同时驱动几何与传动比;WebAudio 合成音效。Vite 产物,源码未入库。
- **human-cell-visualizer**:108k 粒子按索引区间切语义区(前 27% 是外节盘…),单几何体多形态属性 GPU morph(零 CPU 插值),**标注系统:hint 点→最近粒子吸附锚点 + 左右车道卡片 + SVG 贝塞尔能量引线**(纯 DOM 零依赖),按需渲染 dirty-flag(静止零 GPU),内容全在 CELL_INFO/ANNOTATIONS 两张表。
- **algebraic-surface-atlas**:marching tetrahedra 实时网格化隐式曲面,中心差分梯度当法线 + 曲率代理写顶点属性(**度量→颜色教学通道** + 显式图例),拓扑不同不可插值改用噪声溶解转场,配置表 = 图鉴条目。

### 实验(6)
- **bioluminescence**:裸 WebGL2(不用 three),无 VBO 全屏三角形(gl_VertexID),SDF raymarching 花瓣(扇区折叠+smoothUnion 三层),体积积分 Beer 定律 28 步,EMA 帧时 + 硬像素预算的自适应画质。
- **geometry-in-flux**:双形态预烘焙四 attribute GPU morph(每顶点相位错开成波浪),**拓扑距离光涟漪**(76% 参数空间+24% 世界空间,光沿"网格"走),CPU/GPU 双份公式供拾取,canvas.dataset 19 项遥测。
- **Circuit-Board-City**:**矩阵累积→末尾一次 InstancedMesh**(摆放像摆普通 Mesh,实际只存 Matrix4),几何缓存 Map,72 电子沿折线路径插值,电压档=全局光照预设。唯一 Tailwind + 全 minify 构建。
- **home-sweet-home**:**Actor/Form/State 系统**(每实体预建 4 套子树,非当前 scale=0,morph 时抛物弧线+easeOutBack 弹入+逐子错峰),visOf() 父链 scale 连乘当可见度(缩没的物体灯光一起消失),rimify/swayify onBeforeCompile 注入(注意 customProgramCacheKey)。
- **Threejs-3D-Webpage**:Lenis 滚动→单标量 progress 同时驱动相机三关键帧 + 逐瓣相位错峰展开 + 光照/雾/bloom(**滚动叙事最干净范式**);TSL 全局 uniform 节点(一次 JS 赋值全场生效)。唯一默认 forceWebGL=true、`?backend=webgpu` 才开 WebGPU 的保守选择。
- **spider-robot**:Meshy AI 自动绑骨 GLB(Bone_016 编号命名)+ **运行时 CCD IK 8 迭代 + 对角步态**(stance 62% 支撑相 + sin 抬腿),**rest 姿态四元数差 slerp 截断关节限位**(防自动绑骨模型 IK 翻折),不接 GLB 内嵌动画。

## 4. 移植技巧精选(去重后)

**教学交互类(AR 农学直接可用)**:
1. **单参数主时间轴**:机构 = f(t) 纯函数,暂停/变速/倒放/爆炸(正交第二标量)天然成立(X-16)。
2. **固定步长 + 历史环形缓冲**:慢放/单步/scrub/倒带一个机制(Chronograph)——比 mixer.setTime 高一级,快过程(喷头雾化、种子下落)必备。
3. **事件命名字幕**:机构相位→人读动词短语,最低成本高回报(Chronograph)。
4. **标注系统**:hint→最近点吸附锚点 + 车道卡片 + SVG 贝塞尔引线,纯 DOM(Cell)。
5. **Ghost/Section/Isolate 三态**:单 clipping plane + 权重透明度 + damp(X-16)。
6. **数据表 = 课件内容**:同构 JSON 条目,AI 只产出 JSON(四仓共同)。

**场景/氛围类**:
7. **单标量氛围驱动**:nightMix/模式表 + 指数平滑 lerp 全场景(mountain/eiffel)。
8. **shared uniforms 单点真源**:一组 uniform 引用贯穿所有自定义材质,主循环只更新一处(mountain)。
9. **Actor/Form/State 实体重组 morph**:不可插值内容的场景切换(home-sweet-home/Atlas 噪声溶解)。
10. **LOD 删细节层而非降模**:格构建筑 fine 桶整桶距离裁剪(eiffel)。

**资产/动画类**:
11. **程序化骨链动画**:相位递推 bend/pitch + 头反向补偿,救活无动画 AI 模型(Aquatic)。
12. **运行时 CCD IK + 步态 + rest 姿态限位**:驱动自动绑骨 GLB(spider-robot)。
13. **FBX base64 内嵌 + parse 加载**:单文件托管规避二进制请求(sun-temple)。

**工程类**:
14. **遥测三件套**:window.X 全局 + dataset 指标 + URL 参数定状态(全部仓库)。
15. **自适应画质闭环**:EMA 帧时 + 滞回阈值调 DPR/质量档(mountain/bioluminescence/ocean)。
16. **双实现镜像**:JS/TSL 或 CPU/GPU 同函数双写,交互拾取与视觉永远一致(tideglass/geometry-in-flux)。
17. **烘初始状态秒开**:模拟类 demo 预热快照 + 本地复算兜底(coastal)。
18. **矩阵累积→一次 InstancedMesh**(Circuit)+ 按材质 uuid 批合并(tideglass)。

## 5. 对 AR 农学项目的落地清单

1. 时间轴 JSON schema 直接采用 X-16 tour 六元组 {title,text,camera,duration,focus,mode},相机预设加 fitFactor 宽高比适配(竖屏必要)。
2. 讲解系统加"已播状态快照"环形缓冲 → scrub/单步/倒放(Chronograph 模式)。
3. 每条时间轴条目加 `event` 字段,播放时显示机构当前动作的动词短语(事件命名字幕)。
4. 病虫害/农机模型按语义分组,Ghost/Section/Isolate 讲"内部构造";度量→颜色通道讲"病情程度/土壤墒情"并配显式图例。
5. 稻飞虱/蛾子等 AI 生成模型若没动画:程序化骨链(鱼类摆尾公式改扑翼/爬行)+ 头反向补偿,不买动画资产。
6. 给你的 demo/课件留遥测三件套(window 全局 + URL 参数 + dataset),让你和 AI 的对话迭代有反馈回路;每个课件配一个 verify 断言脚本。
7. About 页写诚实声明("示意性模型,非工程复原")。
