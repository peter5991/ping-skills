# 验收工程(verification)

> 来源:motion-web references 蒸馏(2026-09-22)。管"怎么证明动效真的对":截图之外的可执行判据。
> 原则:**数值神谕胜过截图,每个 oracle 只编码一条具体投诉**。

## 神谕(oracle)纪律

1. **一个 oracle 只测一件事**,编码一条具体投诉("只有一个能点开" → 网格扫描各目标点击占比)。**禁用综合质量分**——有案底:六指标合成脚本给所有被人否掉的版本打 6/6,已删。
2. **新 oracle 首轮必须自验**(喂已知答案的输入);有案底:黑帧看门狗读已丢弃的 buffer、双重 sRGB 转换把读数抬高 33%。
3. **渲染路径禁 `Math.random`**(A/B 差分必被污染):改用 per-event 黄金比例 phaser `(start[i] += 0.618×4) % 4`;两次渲染钉同一时钟值才能逐帧差分。
4. **采样率 ≤ 事件时长的 1/5**(6s 事件每 6s 采样 = 测混叠);可见性报"峰值 + 面积"双数;"没变化"的投诉先查尺子分辨率。
5. **帧率无关是声明,须验证**:同一脚本输入跑 30/60/120fps 差分,阈值位置漂移 <0.5、事件时间差 <0.2s 才算过——公式全对而循环里一处忘乘 dt 即假。

## 探针契约(可验收的页面)

动效页内建探针钩子,转场/编排才能被客观检查:

```js
window.__probe = {
  seek(t){ /* 把编排冻结在时刻 t */ },
  hold(t){ /* 停住供测量 */ },
  clock(){ /* 返回当前编排时钟 */ },
};
```

- **转场必须能冻结在任意 t 测量**:headless 截图 ~1s 只抓终态,交接帧 52% 尺寸跳变曾拿着全绿测试过关(判据 |in−out|/out < 3%,测 t=0.002)。
- **churn 测量**(收口"没有动效"的投诉):真实滚轮驱动(非 scrollTo 瞬移),统计动过 transform/opacity 的元素占比——好参考 62% vs 死页 13%。

## 工程陷阱(Failure Patterns 增量)

1. **一属性一 driver**:CSS transition 与 rAF 写同一 transform 属性必打架——同一属性只归一个驱动者。
2. **暂停 ≠ 停积分**:暂停面板开着时积分器照跑(重力/动量暗中累积),须每帧硬重置物理量,而非只停绘制。
3. **ScrollTrigger 在图片加载前初始化**:尺寸全错,须 imagesLoaded 后 `ScrollTrigger.refresh()`。
4. **canvas 改尺寸即清 buffer**:`canvas.width =` 赋值清空全部已绘内容。静态/降级渲染(reduced-motion 单帧)必须监听 resize 重绘;首帧用 rAF 推迟到首次合成后再画(2026-09-23 peter5991 实证:headless 后应用窗口尺寸,同步绘制的帧被清成黑屏)。
5. **headless CLI 截图三坑**(--screenshot + --virtual-time-budget):① 虚拟时间不驱动合成器动画钟,CSS transition/smooth-scroll 被抓在中途(像"入场卡住",实为假象);② 锚点/scrollTo 后的非零滚动位截图必黑,改用**加高窗口整页一次截**(`--window-size=1400,7400`,vh 单位页面临时用静态类压平);③ 窗口最小宽度 500px,390px 移动宽截图右侧必裁——窄屏验收用 DevTools 设备模拟而非 CLI。配合 `--force-prefers-reduced-motion` + 页面自带 `?static` 调试参数(禁动效、压平 vh)可复现静帧验收。
