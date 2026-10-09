# environment.md — 环境与搭建

## 依赖清单(2026-10-08 在 Windows 11 实测通过)

| 依赖 | 版本 | 要点 |
|---|---|---|
| Python | 3.12.10 | **不要用 3.14**:manim 的依赖对它支持不稳。用 `py -3.12` 建 venv |
| manim | 0.21.0 | `--quality` 只接受 l/m/h/p/k 单字母(见 pitfalls #13) |
| manim-slides | 5.7.0 | 课堂版基类 `Slide`/`ThreeDSlide`;`convert` 产 reveal.js 6.0.1 |
| edge-tts | 7.2.8 | `zh-CN-XiaoxiaoNeural`;`SentenceBoundary` 事件给每句 offset/duration(100ns 单位),是字幕同步的数据源 |
| mutagen / numpy | - | 读 mp3 时长 / 数据验算 |
| TeX Live | 宏包见下 | MathTex 依赖;精简安装的 TeX Live 必缺 |
| ffmpeg | 9.0.2 full | 要 full build(带 libass,`subtitles` 滤镜烧字幕);`winget install Gyan.FFmpeg`,装在 `~/AppData/Local/Microsoft/WinGet/Links/`(新 shell 才进 PATH,脚本里用绝对路径兜底) |

TeX 宏包(一次性装齐):

```
tlmgr.bat install standalone preview doublestroke relsize everysel setspace rsfs ragged2e fundus-calligra microtype wasysym physics dvisvgm calligra mathastext
```

- **tlmgr 只在 PowerShell 里有**(`tlmgr.bat`),Git Bash 里没有;报 "tlmgr itself needs to be updated" 时先 `tlmgr.bat update --self`。
- 缺宏包的典型报错:`standalone.cls not found`。

## 搭建

```bash
./tools/manim-env/setup.sh   # Git Bash;建 .venv → pip → tlmgr → 冒烟
```

## 环境坑(全部实踩过)

1. **PYTHONUTF8=1 必须设**:manim-slides `convert` 按系统 GBK 读中文备注,不设就 `UnicodeDecodeError`。模板所有构建脚本已内置 `env["PYTHONUTF8"]="1"`,手工跑命令时别忘。
2. **manim-slides 相对路径按 cwd 解析**(如声音文件):所有命令在课件项目根目录执行,资源路径用绝对路径。
3. **ffmpeg 的 subtitles 滤镜在 Windows 下盘符冒号难转义**:在 srt 所在目录执行、用相对文件名(模板 build_video.py 已处理)。
4. **`rmtree(output/slides)` 报 `PermissionError [WinError 32]`**:某个进程(http.server / 打开课件.bat)的 cwd 就在该目录,Windows 不许删。先停掉占用进程再重建。
5. venv 的 python 与 manim-slides 入口:`tools/manim-env/.venv/Scripts/python.exe` / `manim-slides.exe`。课件项目用 `_env.py` 向上查找仓库根定位,不要写死绝对路径。
