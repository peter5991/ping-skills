# 视觉母版 token

浅色竞赛母版。所有页面共用同一套 CSS 变量,锁定后全套不得漂移。设计基准 1920×1080。

## 色板(token 化,默认医疗绿)

```css
:root{
  --primary:      #159B62;  /* 主色:标题条/标签/图表/描边 */
  --primary-mid:  #54C995;  /* 主色亮阶:次级元素/渐变终点 */
  --primary-bg:   #EAF8F2;  /* 主色浅阶:卡片底/区块底 */
  --accent:       #FF8A28;  /* 强调色:只给关键数字与关键词 */
  --ink:          #1A2B23;  /* 正文深色(向主色微偏,不纯黑) */
  --ink-soft:     #5A6B62;  /* 次要文字 */
  --paper:        #FFFFFF;  /* 页面底 */
  --line:         color-mix(in srgb, var(--primary) 25%, transparent); /* 1px 细线/卡片描边 */
}
```

**换色板**(整套替换前四个色值,气质对应):

| 预设 | --primary | --primary-mid | --primary-bg | --accent | 适用 |
|---|---|---|---|---|---|
| 医疗绿(默认) | #159B62 | #54C995 | #EAF8F2 | #FF8A28 | 医疗/健康/环保/农业 |
| 科技蓝 | #1565C0 | #42A5F5 | #E8F2FC | #FF8A28 | 软件/AI/制造/硬科技 |
| 红旅红 | #C0392B | #E74C3C | #FBEBE9 | #F39C12 | 红旅赛道/公益/乡村振兴 |
| 教育靛 | #2E4A8F | #5B7BD5 | #EBEFF9 | #FF8A28 | 教育/文化/社科 |

自定义:用户给品牌色时以它为 --primary,亮阶/浅阶用 color-mix 推导(`--primary-mid: color-mix(in srgb, var(--primary) 60%, white)`),不手写猜测值。

**纪律**:主色+白底占页面 ≥80%;--accent 只给关键数字、关键词、终极目标收口;禁紫蓝渐变背景、渐变标题字、彩色发光阴影。

## 字号阶梯(1920×1080 基准,vw 换算见 deck-shell.md)

| 层级 | px | 字重 | 用途 |
|---|---|---|---|
| 项目名/封面主角 | 110~150 | 700 | 仅封面与终页 |
| 页标题 | 44~52 | 700 | 每页顶部章节名 |
| 超大数字 | 72~120 | 700 | R4 数字滚动的数据主角 |
| 区块标题 | 28~32 | 600 | 卡片标题/模块标题 |
| 正文 | 20~24 | 400/500 | 说明文字,行高 1.6~1.8 |
| 小注/来源 | 15~17 | 400 | 数据来源/图注,--ink-soft |

中文只用系统栈:`font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif`。数字成列加 `font-variant-numeric:tabular-nums`。

## 统一构件

**页眉(每页固定)**:左侧章节标签(小胶囊,--primary 底白字或白底 --primary 描边)+ 同行页标题;一条 1px --line 细线向右延伸;右上角 IP 图标位(64~80px,全套同一文件)。页眉高度 72px,位置全套统一。

**卡片**:白底、圆角 16~20px、1px var(--line) 描边、阴影 `0 8px 24px rgba(0,0,0,.06)`(只用中性灰影,不用彩色影)。卡片内边距 28~32px。

**标签/胶囊**:标题条用 --primary 实底白字圆角 8px;KPI 胶囊用 --primary-bg 底 --primary 字;竖向分类标签(如「直接就业」)用 --accent。

**地台(可选,全套统一用或不用)**:页面底部浅主色透视梯形/弧形,`background:linear-gradient(to top, var(--primary-bg), transparent)` 加 transform: perspective 斜切,高度 ≤140px,不压内容。

**图表**:柱状图/折线纯 CSS 或内联 SVG,柱体 --primary,最高柱或增长箭头可用 --accent;网格线 --line;坐标文字 --ink-soft 15px。**不生图伪造图表。**

**背景**:--paper 白底,允许极浅径向渐变 `radial-gradient(ellipse at 50% 120%, var(--primary-bg), transparent 60%)` 给底部一点氛围——仅此一处渐变。

## 安全边距与栅格

- 页面安全边距:左右 90px、上 88px(页眉)+ 40px、下 60px;
- 12 列心智栅格,内容区块对齐严格,不碎;
- 每页内容必须在其 1080px 高度内放完,**页内零滚动零溢出**(验收硬指标)。
