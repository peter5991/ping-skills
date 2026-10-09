# recipes.md — Manim 配方库(代码 = templates/recipes.py)

**定位(2026-10-08 二轮修正):参考手册,不是强制约束。** 默认路径 = **模型自行设计动画方案与脚本**(Pi Agent 默认关思考模式,制作动画 Slide 时临时开启;2~3 分钟耗时可接受,详见 jit.md「思考模式」条)。配方库的价值:① 数学类图元直接 import 可用(少写少错);② 写法范本(坐标系怎么建、直线怎么裁剪、正方形怎么保持子对象恒定),模型自行设计时参照。

**回退预案**(负责人备注):若后续实测 Agent 开思考模式耗时过长,则关闭思考、改走"只填配方参数"的约束模式——届时把本文件恢复为强制约束。但当前倾向 = 让模型本身设计动画和脚本。

背景:配方库最初为压 JIT 代码生成耗时而建("Agent 只填数据不写结构")。降级原因:① 并非所有课程都讲数学,M1~M6 覆盖不到的内容强制套配方反而绑手绑脚;② 实测子代理冷启动一次成功,质量够。

## 使用纪律

1. 场景里 `from recipes import *`(在 `from common import *` 之后);数学类内容优先拿配方拼(快且已验证),非数学内容自行设计、可把配方当写法参照。
2. 配方只建图元(mobject),**播放节奏由场景里的 `voice()` 块控制**——动画 run_time 按 yield 出的语音时长 d 分配(自行设计时同样遵守)。
3. 自行设计产出的新图元若可复用,**回收到 recipes.py**(配方库作为参考手册持续积累)。
4. 配色只用 common.py 的设计令牌(BG/INK/MUTED/ACCENT/GOOD/WARN/DATA…),不在场景里发明颜色、不用 manim 出厂色(自行设计同样遵守;字级用 SIZE_TITLE/BODY/NOTE 阶梯)。

## 配方清单

| # | 配方 | 函数 | 要点 |
|---|---|---|---|
| M1 | 教学坐标系 | `axes_2d(x_range, y_range, width, height, x_label, y_label, tick_step_x, tick_step_y)` | 灰轴无箭头;轴标题用 T() 系统字体 |
| M2 | 数据点 | `dots(ax, xs, ys, color, r)` | |
| M3 | 直线 | `line_kb(ax, k, b, color, x0, x1, sw)` | **自动按 y 范围裁剪**,陡峭线不出框(pitfalls #4) |
| M4a | 残差线段 | `residual_segs(ax, k, b, xs, ys)` | 竖直方向(预测方向),非最短距离 |
| M4b | 残差正方形 | `residual_squares(ax, k, b, xs, ys, opacity)` | 面积 ∝ 误差²;**子对象数量恒定**(0 残差用极小占位,动画插值需要结构一致,pitfalls #1);装不下时整体等比缩小并注明(面积比例不变) |
| M5 | 标题组 | `title_group(title, subtitle)` | 播放:`Write(t[0])` → `FadeIn(t[1], shift=UP*0.2)` |
| M6 | 推导步进 | `derive_chain(formulas, scale)` | 播放:第一个 `Write`,之后 `TransformMatchingTex(steps[i], steps[i+1])` 逐步变形;每步一个 voice 段 |

辅助:`y_unit(ax)` = y 轴 1 数据单位的屏幕长度,画"真正的正方形"类等比图形必用。

## 典型播放模式(场景骨架)

```python
class P02Data(Lesson):
    def body(self):
        ax, ds = axes_2d(x_label="学习时长(小时)", y_label="分数"), None
        ds = dots(ax, X, Y)
        with self.voice("p2_data") as d:
            self.play(Create(ax), run_time=d * 0.4)
            self.play(LaggedStart(*[FadeIn(p, shift=DOWN) for p in ds], lag_ratio=0.2), run_time=d * 0.5)
        ln = line_kb(ax, K, B)
        with self.voice("p2_line") as d:
            self.play(Create(ln), run_time=d * 0.6)
```

## 待萃取(用过才回收,不预先设计)

- 3D 曲面/碗(least_squares S06Bowl 的 ThreeDSlide + 切片演示)
- 数轴+可吸附标记(mean.html 的 Manim 版)
- 表格逐行高亮(S07Compute 的计算表)
