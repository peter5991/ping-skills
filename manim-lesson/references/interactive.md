# interactive.md — 交互教具页范式

嵌在课堂版 reveal.js 里的教具页:**纯 SVG + vanilla JS,零框架**,学生上台拖、教师控制节奏。范本 = 最小二乘法项目的 `web/squares.html`(拖直线压残差平方总面积)与 `web/mean.html`(拖 c 找平均数)。

## 共享层 `web/shared.js` / `shared.css`

- `el(tag, attrs, parent)` 建 SVG 元素;`scale(d0,d1,r0,r1)` 线性比例尺(带 `.inv` 逆变换和 `.k` 像素/单位)
- `svgPoint(svg, evt)` 屏幕坐标→viewBox 坐标;`draggable(node, svg, onMove, onEnd)` 基于 **pointer capture** 的拖拽
- `axes(g, sx, sy, xticks, yticks)` 画坐标轴;`tex(node, s)` 渲染 KaTeX(无 katex 时降级纯文本)
- **翻页桥**:iframe 内键盘事件到不了父页面,shared.js 把方向键/空格 `postMessage({type:'reveal-nav'})` 转给父页;build_slides.py 注入的 BRIDGE 接收后调 `Reveal.next/prev`,并在 `slidechanged` 时 `window.focus()` 把焦点还主页面。滑块(`input[type=range]`)自己的方向键不转发
- 配色与 Manim 侧 common.py **同一组设计令牌**(bg/panel/ink/muted/good/warn/data/accent,--accent 随该课主色同步),动画页与教具页视觉连续

## 教学手法(已验证有效)

1. **拖动手柄直接操作数学对象**:手柄在线上,拖即改 k/b;读数大字实时更新(`tabular-nums`)。
2. **目标函数侧栏曲线**:主图旁边挂"目标量随参数变化"的小图(如 Σe²–k 抛物线),拖动时红点沿曲线实时移动并留下**拖动轨迹**——把抽象的优化目标变成看得见的游戏。曲线是"给定 k 时最优 b"的剖面;自由拖动模式下点会落在曲线上方,图表标题要注明(数学上是对的,别当 bug 修)。
3. **本节课最佳**:记录学生拖出的历史最优值并显示——天然形成课堂挑战。
4. **教师节奏控制按钮**:"揭晓答案"(动画缓动移到最优解,`animateTo` ease-in-out)、"加入异常值"(现场演示鲁棒性)、"重置"。讲到哪按哪,不自动播。
5. **最优解附近吸附**:手拖停不到精确的导数为零点,靠近目标(平均数/中位数)< 阈值时 snap 过去。
6. **模式切换**:单手柄(绕重心旋转)/双手柄(自由拖动)这类约束切换,帮学生隔离变量。

## 已踩坑(根因与对策)

| # | 症状 | 根因 | 对策 |
|---|---|---|---|
| 1 | 拖动一次后就拖不动 | 每次 draw() 重建点/手柄 DOM,pointer capture 随旧节点丢失 | **拖动中的元素常驻,只更新属性不重建** |
| 2 | 图形画到侧栏面板里 | svg `overflow:visible`,clipPath 范围不对 | clipPath 精确等于绘图区(如 sx(0)..sx(6.5)) |
| 3 | c 停在中位数上,"左点数−右点数"≠0 | 浮点平均数 1.50999… 让相等点算到一侧 | c 与吸附目标统一取到 0.0001,切模式时重新吸附 |
| 4 | 曲线谷底被压平 | 纵向比例由远端大值决定 | 比例只按"数据 + 当前参数 ± 余量"的局部范围定,超出顶部不画 |
| 5 | 标签重叠 | 按数据下标交错 | 按**在数轴上的排序**交错;标记标签上移到数据标签之上 |
| 6 | 显示 "−0" / "−0.0" | 浮点负零 | 格式化先 round 再 +0.0;绝对值小于阈值显示 0 |

## 硬约束

- **禁 CDN**:KaTeX 引用产物内 `katex/` 相对路径(build_slides.py 从 `assets/lesson/libs/katex` 复制);教室可能无网。
- 配色走 shared.css 变量,深色底;读数三米外可读;手柄触摸区够大(transparent rect 扩大热区)。
- 数值与 Manim 侧、data.py 三方一致——教具页的基准数据从 data.py 抄入后用断言核对(最优解、SSE 等)。
