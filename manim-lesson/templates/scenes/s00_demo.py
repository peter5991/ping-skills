import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import *


class S00Demo(Lesson):
    """最小演示:两段旁白、一个分步点。跑通后替换成正式内容。"""

    def body(self):
        title = T("演示课件", SIZE_TITLE).shift(UP * 1.2)
        with self.voice("s0_title") as d:
            self.play(Write(title), run_time=min(1.5, d * 0.5))
        formula = MathTex(r"e_i = y_i - \hat{y}_i", color=ACCENT).scale(1.6).shift(DOWN * 0.6)
        with self.voice("s0_point") as d:
            self.play(FadeIn(formula, shift=UP * 0.2), run_time=min(1.2, d * 0.5))
        self.fade_all()
