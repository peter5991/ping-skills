# templates — Manim 课件项目脚手架

开新项目:

1. 先在 `output/manim-lessons/<主题>/SCRIPT.md` 写教学脚本(骨架 = `templates/SCRIPT.md`),教师过目后再动工;
2. 复制模板:

```bash
mkdir -p output/manim-lessons/<主题>
cp -r .claude/skills/manim-lesson/templates/* output/manim-lessons/<主题>/
rm output/manim-lessons/<主题>/SCRIPT.md   # 骨架会覆盖第 1 步写好的 SCRIPT.md,复制后删掉骨架(2026-10-08 血泪:同名覆盖过一次)
# 本 README 可以不复制
```

然后按 SKILL.md 工作流:SCRIPT.md → narration.py → data.py → `python tts.py` → 逐幕写 scenes/ → `./render_ql.sh` 低画质迭代 → build_video.py / build_slides.py 出双产物。

模板自带一个最小演示场景 `scenes/s00_demo.py`(两段旁白、一个 step),先跑通它验证管线,再替换成正式内容。
