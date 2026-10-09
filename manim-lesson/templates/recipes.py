"""Manim 配方库:参数化教学图元,Agent 只填数据不写结构。

配套文档:.claude/skills/manim-lesson/references/recipes.md(选型/参数/红线)。
配方 = least_squares 项目实战验证过的图元泛化;与 common.py 的设计令牌/T()/fmt() 配套。
依赖:from common import *(令牌、T、fmt),from manim import *。
"""
import numpy as np
from manim import *

from common import T, DATA, ACCENT, WARN, MUTED, INK, SIZE_TITLE, SIZE_BODY, SIZE_NOTE


# ---------- M1 坐标系 ----------

def axes_2d(x_range=(0, 6, 1), y_range=(40, 100, 10), width=6.5, height=5.0,
            x_label=None, y_label=None, tick_step_x=1, tick_step_y=10, font_size=24):
    """教学坐标系。labels 给字符串则加轴标题(如 "学习时长(小时)"/"分数")。"""
    ax = Axes(
        x_range=list(x_range), y_range=list(y_range),
        x_length=width, y_length=height,
        axis_config={"color": MUTED, "include_tip": False, "font_size": font_size},
        x_axis_config={"numbers_to_include": range(int(x_range[0]) + (1 if x_range[0] == 0 else 0), int(x_range[1]) + 1, tick_step_x)},
        y_axis_config={"numbers_to_include": range(int(y_range[0]), int(y_range[1]) + 1, tick_step_y)},
    )
    if x_label:
        ax.add(T(x_label, SIZE_NOTE, MUTED).next_to(ax.x_axis, DOWN, buff=0.35))
    if y_label:
        ax.add(T(y_label, SIZE_NOTE, MUTED).next_to(ax.y_axis, UP, buff=0.15))
    return ax


def y_unit(ax):
    """y 轴 1 个数据单位对应的屏幕长度。画"真正的正方形"等需要等比图形时用。"""
    return ax.c2p(0, ax.y_range[0] + 1)[1] - ax.c2p(0, ax.y_range[0])[1]


# ---------- M2 数据点 ----------

def dots(ax, xs, ys, color=DATA, r=0.08):
    return VGroup(*[Dot(ax.c2p(x, y), radius=r, color=color) for x, y in zip(xs, ys)])


# ---------- M3 直线(按坐标系 y 范围裁剪,陡峭线不会画出框) ----------

def line_kb(ax, k, b, color=ACCENT, x0=None, x1=None, sw=4):
    x0 = ax.x_range[0] if x0 is None else x0
    x1 = ax.x_range[1] if x1 is None else x1
    if abs(k) > 1e-9:
        lo, hi = sorted(((ax.y_range[0] - b) / k, (ax.y_range[1] - b) / k))
        x0, x1 = max(x0, lo), min(x1, hi)
    return Line(ax.c2p(x0, k * x0 + b), ax.c2p(x1, k * x1 + b), color=color, stroke_width=sw)


# ---------- M4 残差(线段 / 真实正方形) ----------

def residual_segs(ax, k, b, xs, ys, color=WARN):
    """竖直残差线段(预测方向上的误差,不是点到直线最短距离)。"""
    return VGroup(*[Line(ax.c2p(x, y), ax.c2p(x, k * x + b), color=color, stroke_width=3)
                    for x, y in zip(xs, ys)])


def residual_squares(ax, k, b, xs, ys, color=WARN, opacity=0.35):
    """以残差为边的真实正方形(面积 ∝ 误差²,最小二乘的签名图示)。
    子对象数量恒定(残差为 0 用极小正方形占位)——动画插值需要结构一致。"""
    u = y_unit(ax)
    out = VGroup()
    for x, y in zip(xs, ys):
        e = y - (k * x + b)
        side = max(abs(e) * u, 1e-3)
        p_pred = ax.c2p(x, k * x + b)
        p_true = ax.c2p(x, y)
        lo = p_pred if e > 0 else p_true
        sq = Rectangle(width=side, height=side, stroke_color=color, stroke_width=2,
                       fill_color=color, fill_opacity=opacity)
        sq.move_to(lo + np.array([side / 2, side / 2, 0]))
        out.add(sq)
    return out


# ---------- M5 标题页 ----------

def title_group(title, subtitle=None, title_size=SIZE_TITLE):
    """居中标题组;播放模式见 recipes.md(Write → FadeIn)。"""
    t = T(title, title_size).shift(UP * 1.2)
    if subtitle:
        sub = T(subtitle, SIZE_BODY, MUTED).next_to(t, DOWN, buff=0.35)
        return VGroup(t, sub)
    return VGroup(t)


# ---------- M6 公式推导步进 ----------

def derive_chain(formulas, scale=1.2, color=INK):
    """一串 MathTex 推导步骤,居中排列;用 TransformMatchingTex 逐步变形(播放模式见 recipes.md)。
    formulas: LaTeX 字符串列表,如 [r"S = \\sum (x_i - c)^2", r"\\frac{dS}{dc} = 0", ...]"""
    steps = [MathTex(f, color=color).scale(scale) for f in formulas]
    return VGroup(*steps)
