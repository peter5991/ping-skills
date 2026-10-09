"""所有场景共用:配色、字体、Lesson 基类(视频/课堂两种模式)。

机制详解见 .claude/skills/manim-lesson/references/architecture.md。
图元函数(坐标系/点/线/残差等)按课题需要自行添加——最小二乘法项目的
score_axes/dots/line_kb/residual_squares 可作参考,注意直线要按坐标系 y 范围裁剪。
"""
import json
import os
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import *
from manim_slides import Slide, ThreeDSlide

from narration import ALL, SCRIPT, step_notes

ROOT = Path(__file__).resolve().parent
MODE = os.environ.get("LS_MODE", "video")  # video | slides | jit(每页独立片段:按语音时长 pacing,不烤声音,结尾不清屏)
DURATIONS = json.loads((ROOT / "audio" / "durations.json").read_text("utf-8"))
CUE_DIR = ROOT / "build" / "cues"

# 设计令牌(与 web/shared.css 同一组值,教具页与动画页视觉连续)
# 纪律:场景只用这里的令牌,不发明颜色、不用 manim 出厂色(尤其禁 #FFFF00 纯黄);
# 一课一主色——每课在 SCRIPT.md §2.5 从候选里选一个 ACCENT 填回这里,其余不动。
BG       = "#0B0D10"  # 近黑底:禁纯黑(投影上发灰发死),与课堂版网页底色一致
PANEL    = "#14181D"  # 面板/底板
HAIRLINE = "#2A3038"  # 细线/边框/辅助网格
INK      = "#E8E8E8"  # 主文字(不用纯白,投影更柔)
MUTED    = "#9AA3AD"  # 次要文字/注脚/坐标轴
GOOD     = "#83C167"  # 语义:正确/达成
WARN     = "#F26D5B"  # 语义:误差/警告(残差也用此色)
DATA     = "#7E9CB5"  # 数据点等次主角图元(让位于主色)

# 主色候选:主角图元(拟合线/关键公式/结论框)用,一屏一个焦点
ACCENT_CYAN  = "#5FB4CC"  # 青(默认,数理课中性)
ACCENT_MINT  = "#7FC8A9"  # 薄荷
ACCENT_GOLD  = "#D9A441"  # 金
ACCENT_CORAL = "#E8845C"  # 珊瑚
ACCENT = ACCENT_CYAN

FONT = "Microsoft YaHei"

# 字级阶梯(投影可读下限,不再小)
SIZE_TITLE = 48
SIZE_BODY  = 32
SIZE_NOTE  = 22

config.background_color = BG

SUB_SAFE_Y = -3.0  # 此线以下留给烧录字幕,不放内容
PAUSE = 0.8        # 视频模式中每段旁白后的停顿(给观众消化的时间)


def T(s, size=SIZE_BODY, color=INK, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def fmt(v, signed=False, nd=0):
    """格式化数字,避免出现 "-0"。"""
    v = round(float(v), nd) + 0.0
    return (f"{v:+.{nd}f}" if signed and v != 0 else f"{v:.{nd}f}")


class _LessonMixin:
    skip_reversing = True  # 课堂版不需要倒放片段,渲染量减半

    def __init__(self, *args, **kwargs):
        # 两种模式各用各的 manim-slides 输出目录,可以并行构建而互不覆盖
        super().__init__(*args, output_folder=ROOT / "build" / f"slides_{MODE}", **kwargs)

    def setup(self):
        super().setup()
        self.cues = []
        self._pre = None  # 课堂模式:已经提前切好步的旁白 key

    first_key = None  # 本场景第一段旁白(默认取本幕第一段;一幕拆成多个场景时由子类指定)

    @contextmanager
    def voice(self, key, slide_d=None):
        """一段旁白。块内动画可以用 yield 出的时长 d 分配 run_time。

        video:播放配音;块结束后若动画短于语音,补 wait。
        slides:不放声音。分步点放在"上一段旁白结束之后",
                这样两段旁白之间的过渡动画(淡出、移位)属于下一步,每一步都停在内容完整的画面上。
        jit:同 video 的时长 pacing(动画按完整语音时长分配),但不烤声音
            (语音由 JIT 播放器独立播放),结尾留 0.5s 余量供循环。
        """
        n = ALL[key]
        dur = DURATIONS[key]["duration"]
        if MODE == "video":
            start = self.renderer.time
            self.add_sound(DURATIONS[key]["path"])
            self.cues.append([key, start])
            yield dur
            remaining = dur - (self.renderer.time - start)
            self.wait(max(remaining, 0) + PAUSE)
        elif MODE == "jit":
            start = self.renderer.time
            yield dur
            remaining = dur - (self.renderer.time - start)
            self.wait(max(remaining, 0) + 0.5)
        else:
            if n.step and self._pre != key:
                self.next_slide(notes=step_notes(self.scene_id, key))
            self._pre = None
            yield slide_d or float(np.clip(dur * 0.45, 1.2, 4.0))
            items = SCRIPT[self.scene_id]
            i = next(j for j, m in enumerate(items) if m.key == key)
            if i + 1 < len(items) and items[i + 1].step:
                self.next_slide(notes=step_notes(self.scene_id, items[i + 1].key))
                self._pre = items[i + 1].key

    def pause(self, t=1.0):
        """视频中的纯停顿(课堂版不需要,因为老师控制节奏)。"""
        if MODE == "video":
            self.wait(t)

    def step_break(self, notes=""):
        """课堂版中额外的分步点(不对应旁白)。"""
        if MODE == "slides":
            self.next_slide(notes=notes)

    def fade_all(self, run_time=1.0):
        """场景结尾清屏。课堂版/JIT 跳过:课堂版否则最后一步停在黑屏;JIT 页要停住供循环。"""
        if MODE == "video":
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    def construct(self):
        if MODE == "slides":
            first = self.first_key or SCRIPT[self.scene_id][0].key
            self.next_slide(notes=step_notes(self.scene_id, first))  # 不产生空页,只为第一页设置备注
            self._pre = first
        self.body()
        if MODE == "video":
            self.wait(0.5)
            CUE_DIR.mkdir(parents=True, exist_ok=True)
            (CUE_DIR / f"{type(self).__name__}.json").write_text(json.dumps(self.cues), "utf-8")

    @property
    def scene_id(self):
        return type(self).__name__[:3]  # "S00Demo" -> "S00"


class Lesson(_LessonMixin, Slide):
    pass


class Lesson3D(_LessonMixin, ThreeDSlide):
    pass
