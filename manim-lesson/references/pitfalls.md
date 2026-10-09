# pitfalls.md — 已踩坑清单与验证技术

全部来自最小二乘法项目实战(2026-10-08),按"症状 → 根因 → 对策"记录。出 bug 先查这里。

## Manim 场景

1. **`ValueError: zip() argument 2 is shorter than argument 1`**(对 `always_redraw` 生成的对象做 FadeIn):动画开始后对象被重建,子对象数量和 FadeIn 保存的起始副本不一致。→ 直线静止的那一段改用静态 VGroup;需要结构恒定时(如 5 个残差正方形)用极小占位元素保证**子对象数量恒定**。
2. **显示 "−0"**:`f"{-0.0:.0f}"` 输出 "-0"。→ 统一走 `fmt()`(先 round 再 +0.0)。
3. **3D 场景里 `add_fixed_in_frame_mobjects` 的文字在镜头复位后位置错乱**。→ 不在 3D 场景里硬调,把二维推导拆成独立的 2D 场景(scene_id 相同,旁白分步不受影响)。
4. **陡峭直线画出坐标系**。→ 直线按坐标系 y 范围裁剪后再画(common.py `line_kb` 的做法)。
5. **bash heredoc 里写 Python 替换脚本,`\f` `\a` 被当转义字符**(`\frac` 变换页符)。→ 含反斜杠的修改一律用编辑工具,或 `chr(92)`。

## 课堂版(manim-slides)

6. **每一步结束都是黑屏/空画面**:`next_slide` 放在旁白开头,上一步的收尾动画(含结尾淡出)被算进当前页结尾。→ 分步点放在**一段旁白播完之后**;场景结尾淡出 `fade_all()` 只在 video 模式执行。`next_slide` 之后没有动画不会产生空页。
7. **HQ 构建静默失败(严重)**:manim-slides 自己的 click 解析器有 `-h`(help),`-qh` 被拆成 `-q -h`,打印帮助后以 0 退出,`check=True` 发现不了;convert 悄悄用上次留下的旧 json,产出一份"成功"的低清课件。→ **`--quality h` 分开传参**;每幕渲染后断言产物 json 的 mtime 晚于构建起点(模板 build_slides.py 已内置,fail-loud)。
8. **`rmtree` 报 `PermissionError [WinError 32]`**:测试用 http.server 的 cwd 就在要删的目录。→ 先停占用进程;老师开着 `打开课件.bat` 时重建也会撞,先关那个窗口。
9. manim-slides `next_slide(notes=...)` 的备注属于**下一张**幻灯片;`convert` 读中文备注要 `PYTHONUTF8=1`。
10. **convert 产物默认引 jsdelivr CDN 的 reveal.js,断网即整页白屏**(2026-10-09 实测 ERR_CONNECTION_RESET,`Reveal is not defined`):教室网络不可控,课堂版必须离线。→ reveal.js 6.0.1 vendor 进 `templates/web/vendor/revealjs/`(来源 npmmirror tarball `registry.npmmirror.com/reveal.js/-/reveal.js-6.0.1.tgz`,取 dist/{reveal.js,reveal.css,theme/black.css,plugin/{markdown.js,notes.js,highlight/zenburn.css}});build_slides.py 把 CDN 前缀改写为 `vendor/revealjs` 并断言生效。注意 `--offline` 选项只是构建时下载,CDN 断了照样失败,vendor 才是根治。

## 交互页

见 interactive.md 的坑表(pointer capture/clipPath/浮点吸附/比例压平/标签交错/负零)。

## 时长与节奏

- 语速 −10%、句间停顿 0.8 s、提问后加 `pause(3)` 等,是教师节奏感的主要旋钮;纯语音时长 × 动画停顿 ≈ 成片时长,低画质整片拼一次就能估。
- slides 模式动画时长 = 语音时长 × 0.45 钳制 1.2–4 s(common.py voice()),课堂版不要太慢。

## 验证技术(不靠眼睛耳朵,靠数据)

11. **缩略图拼图逐帧过目**:`preview.sh <视频> <png> [间隔秒]` 用 ffmpeg tile 滤镜出 4x4 拼图,低画质迭代时全靠它。
12. **黑帧检测**:ffmpeg 取每页最后一帧查亮度(signalstats YMAX),确认没有停在黑屏。注意**别加 `-v error`**——它会把 info 级的 metadata 输出也屏蔽,测出一堆 0 造成误判。
13. **音画同步**:对成片跑 `silencedetect`(-35 dB、0.25 s)得语音起点,逐条字幕比对最近起点偏差:中位数应在 ±0.2 s 内;**前/中/后三段分别算中位数查累积漂移**;偏差大的通常是长句切半的后半行(语音中间无停顿,检测不到起点),属预期。
14. **页数断言**:convert 后 HTML section 数 == 各幕 json 页数合计 + 插入的交互页数,不相等直接报错(模板已内置)。
15. **交互页实测**:Chrome(chrome-devtools MCP)用真实 PointerEvent 序列模拟拖动,elementFromPoint 验证手柄可命中;iframe 内按方向键验证翻页转发;console 零报错(favicon 404 除外)。
