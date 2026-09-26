# 范本案例:AutoPiano 3D 钢琴(可交互 3D 乐器/产品)

> 来源:2026-09-24 对 https://www.autopiano.cn/zh-TW/3d 线上 bundle 实测(Nuxt SSR + webpack 懒加载 chunk,逐 chunk 指纹分析;CDN 有 Referer ACL,抓包须带 `-e https://www.autopiano.cn/`)。
> 一句话:**可交互 3D 乐器 = 程序化建模 + 弹簧物理按键 + 采样音频 + 拾取白名单,全程零美术资产、零模型文件**。

## 0. 什么时候用这个范本

做"可上手玩的 3D 物件"(乐器、产品拆解、机械演示)时照抄本范本的分层:**模型程序化生成 → 交互部件挂 pivot + 弹簧 → Raycaster 白名单拾取 → 音频走采样表**。不要做的情况同 T2 红线(生成速度硬约束/低端设备)。

## 1. 架构:3D 是懒加载子系统,不是页面本体

- 首屏 SSR 只含 UI 壳 + loading 卡(分阶段文案:"正在準備舞台與琴體…");Three.js/Tone.js/场景逻辑全部拆进动态 chunk,进入页面才拉取。
- 对离线单文件场景的翻译:库本地化后,**场景初始化放在首次交互或 `requestIdleCallback` 后**,loading 卡给分阶段文案,别让白屏等 WebGL。
- AudioContext 必须首次用户手势解锁(浏览器 autoplay 策略),解锁前所有发声调用入队。

## 2. 模型:全程序化建模(本站最大的反直觉点)

**没有用 glTF/GLB——整台三角钢琴是 Three.js 图元在代码里拼出来的。** 证据:全 bundle 无 GLTFLoader 实例化,节点命名全是语义化工件:`piano-key-*`、`piano-key-pivot-*`、`piano-leg-column-*`、`piano-caster-wheel-*`、`piano-overhead-spotlight`。

可照搬的纪律:

1. **参数化布局 + 断言**:琴体宽度、键盘宽度全是参数,构造期断言(如"琴壳宽度必须容纳完整键盘框"),布局错了当场炸,不静默渲染错位。
2. **每个可交互部件 = pivot Group + 子 Mesh**:键的 pivot 定位在键根(支点),动画只转 `pivot.rotation.x`,子网格只管造型。
3. **换肤 = 调色板切换,不是换模型**:四套皮肤(象牙白/曜石黑/樱花粉/梦幻蓝)只是材质色板+mood 灯光参数,零资产。
4. 键盘规格照实物:88 键 / 52 白键,黑键在 pivot 上加 `blackKeyLift` 抬升。

## 3. 按键手感:阻尼弹簧(角运动),不是补间

按下/回弹共用一条弹簧方程,按方向换参数:

```js
// update(dt) 内,对每个 animatingKey:
const pressing = key.targetAngle < 0;
const k = pressing ? 205 : 145;   // 刚度:按下更脆
const c = pressing ? 22 : 17.5;   // 阻尼
const d = (key.targetAngle - key.angle) * k - key.angularVelocity * c;
key.angularVelocity += d * dt;
key.angle += key.angularVelocity * dt;
// 静止吸附(防抖 cutoff,同 T0-6 红线):
if (!pressing && Math.abs(key.angle) < 8e-5 && Math.abs(key.angularVelocity) < .002) {
  key.angle = 0; key.angularVelocity = 0;
}
key.pivot.rotation.x = key.angle;
```

高亮发光与弹簧解耦,走 `THREE.MathUtils.damp`(帧率无关):

```js
key.highlight = THREE.MathUtils.damp(key.highlight, key.highlightTarget, key.highlightTarget ? 18 : 10, dt);
key.mesh.material.color.copy(key.restColor).lerp(key.highlightColor, key.highlight);
// + emissive 同步提亮
```

要点:**按下和松开用不同 λ(18/10)**——亮起快、熄灭慢,手感"跟手但不闪烁"。

## 4. 拾取:Raycaster + 白名单数组

```js
pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
raycaster.setFromCamera(pointer, camera);
const hit = raycaster.intersectObjects(pickableKeys, false)[0]; // 白名单,不递归全场景
return hit ? hit.object.userData.noteName : null;
```

- `pickableKeys` 是平铺数组,`recursive=false`,88 个对象的拾取成本可忽略;**别对整场景递归 raycast**。
- 命中信息存在 `userData`(noteName/midi),不查表反推。

## 5. 镜头:三预设 + 同步缓动切换

| 预设 | position | target |
|---|---|---|
| showcase(侧视) | (-10.8, 8.2, -17.8) | (0, 1.1, 3.25) |
| play(正视) | (-1.8, 5.4, -15.8) | (0, 1.3, -0.4) |
| top(俯视) | (-5.2, 28, -1.5) | (0, 1, 3.6) |

```js
// 切换:1.05s ease-out cubic,position 与 controls.target 同步 lerp(只挪 position 不挪 target = 镜头甩头)
progress = Math.min(elapsed / 1.05, 1);
const k = 1 - Math.pow(1 - progress, 3);
camera.position.lerpVectors(startPos, endPos, k);
controls.target.lerpVectors(startTarget, endTarget, k);
```

- fov = **36**(长焦压缩纵深,与 T2 工程要点"长焦是画面感的单点杠杆"互证)。
- OrbitControls:`enableDamping, dampingFactor=.055, minDistance=12, maxDistance=40, polar ∈ [.08π, .5π]`(禁钻到琴底/正顶)。
- 属性级小补间(灯光强度等)用 ease-in-out cubic:`p<.5 ? 4p³ : 1-(-2p+2)³/2`——与镜头切换的 ease-out 分工明确:**入场/切换 ease-out,状态往返 ease-in-out**。

## 6. 灯光氛围:同色雾 + 半球光 + 可见光锥

- 背景与雾同色:`bg = fog = 0xF8F5EF`(暖白),`Fog(0xF8F5EF, 28, 58)`——远景消隐进背景色,零成本的纵深。
- 主光:`HemisphereLight(0xFFFFFF, 0xD6C8B8, 1.75)`(天光白/地面暖米);`DirectionalLight` 唯一投影源,`shadow.mapSize=1024`、负 bias(-0.00035)防条纹。
- 聚光灯默认关,打开才建:`SpotLight(angle=.12π, penumbra=.68, decay=1.28)` 挂 (0,30,3.2);**可见光柱 = 两个半透明锥体**(半径 11.4/6.4、高 28.5,`transparent, opacity 渐变, depthWrite:false, renderOrder 1/2`)——不用体积光/后处理,锥体网格就够。
- 开灯/换肤时**所有颜色指数阻尼趋近目标**:`λ = 1 - exp(-3.2*dt)`,逐帧 `light.color.lerp(mood.target, λ)`——帧率无关,任意中断都平滑。

## 7. 音频:Tone.js Sampler + 每键采样映射

- 引擎是 Tone.js(libs.md 已收录);每键一条采样文件,键位表即数据源:

```js
{ id: 10, name: 'E3', singName: 'mi', keyCode: '48', key: '0', fileName: 'a48.mp3', type: 'white', char: '0' }
```

- 36 个 mp3 采样覆盖 88 键(相邻半音由 Sampler 插值/pitch 微调),比 88 个全采样省一半以上加载量。
- 键位映射可插拔:三套电脑键盘布局(Standard/FreePiano/FlashPiano)只是换 keymap 表,发声层不动。
- 松键包络:`releaseDelay=200ms`、尾部 `duration≈5s`;全局 `volumeFactor=.8` 防削波。
- MIDI 输入 = Web MIDI API(`navigator.requestMIDIAccess`),另带模拟器兜底(HTTP 环境/无设备时自弹试音)。

## 8. 特效:对象池粒子 + InstancedMesh 音轨

- 琴键特效(off/红蓝眼泪/音轨线/流光花瓣/气泡/音符)= **一套自定义 ShaderMaterial 粒子池**:`Float32Array` 预分配(2800 粒子)、ring cursor 复用、颜色在池内按 palette 预烘(deep→bright→pale 三段 lerp + 随机扰动),切特效只换 palette 不重建池。
- 持续按压脉冲:按住时每 **0.18s** 向活跃音补喷一波粒子。
- 音轨线(trail)= **InstancedMesh**:`instanceMatrix.setUsage(DynamicDrawUsage)`、`frustumCulled=false`(实例位置靠 CPU 矩阵,包围球失真必须关剔除)、槽位 acquire/release 复用。
- 舞台特效与琴键特效分两层:geometry = 琴体共振发光网格,fireworks = 独立粒子发射器,互不共享池。
- 粒子 shader 内 dpr 上限 2,渲染器上限 1.5(见下)。

## 9. 性能与生命周期红线(实测值)

| 项 | 取值 | 理由 |
|---|---|---|
| renderer pixelRatio | `min(max(dpr,1), 1.5)` | 高分屏 3D 的第一杀手是填充率 |
| 粒子 shader dpr uniform | ≤ 2 | 点尺寸视觉等效,不必全分辨率 |
| 页面隐藏 | `visibilitychange` → `pageVisible=false` 停特效循环 | 后台标签零消耗 |
| 销毁 | `cancelAnimationFrame` + 全部 `removeEventListener` + 三件套 dispose | SPA 路由切换不泄漏 |
| 拾取 | 白名单数组 + `recursive=false` | 见 §4 |

## 10. 滥用红线

1. **先问要不要 3D**:2D 琴键 + CSS 弹簧能覆盖教学/工具场景的 80%;本范本只用于"3D 本身就是卖点"的页。
2. 程序化建模只适用于**形态规则、可参数化**的物件(乐器/家具/机械);有机形体老老实实用 glTF。
3. 音频采样文件必须本地化(红线 #3);MIDI/麦克风等权限 API 要有无权限降级路径。
4. 持续特效最多一层常开(编排放纪律);粒子池大小写死,不随输入无限增长。
