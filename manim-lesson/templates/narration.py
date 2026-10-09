"""全部旁白。

每幕是一个有序列表,元素 N(key, text, speak=None, step=False):
- text   字幕文本(画面上显示)
- speak  朗读文本(给 TTS);省略则与 text 相同。两者必须按 。!? 切出相同句数(tts.py 会断言)。
- step   课堂版中,这句话是否开启新的一步(next_slide)。同一步内的所有旁白合并为演讲者备注。

数字/公式在 speak 里改成中文读法,如 "y = 68" → "y等于68"、"124 分" → "一百二十四分"。
"""
from collections import namedtuple

N = namedtuple("N", "key text speak step", defaults=(None, False))

SCRIPT = {
    "S00": [
        N("s0_title", "这是演示课件的开场白,替换成你的第一课。", step=True),
        N("s0_point", "这是第二段旁白,和上一段属于同一步,课堂版里不会翻页。"),
    ],
}

ALL = {n.key: n for scene in SCRIPT.values() for n in scene}
assert len(ALL) == sum(len(s) for s in SCRIPT.values()), "key 重复"


def speak_of(n):
    return n.speak or n.text


def step_notes(scene, key):
    """从 key 开始,到下一个 step=True 之前,所有旁白拼成演讲者备注。"""
    items = SCRIPT[scene]
    i = next(j for j, n in enumerate(items) if n.key == key)
    out = [items[i].text]
    for n in items[i + 1:]:
        if n.step:
            break
        out.append(n.text)
    return "\n\n".join(out)
