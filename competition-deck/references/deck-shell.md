# 16:9 翻页壳规范

单个 `index.html` 容纳全部 slide。设计基准 1920×1080,按窗口等比缩放居中。

## 壳结构(骨架模板)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>项目名 — 路演 deck</title>
<style>
  /* token(照抄 visual-tokens.md 锁定版) */
  html,body{margin:0;height:100%;overflow:hidden;background:#0d0f0e;font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif}
  #stage{position:fixed;left:50%;top:50%;width:1920px;height:1080px;transform-origin:center;background:var(--paper)}
  .slide{position:absolute;inset:0;display:none;padding:88px 90px 60px}
  .slide.on{display:block}
  /* 页码 */
  #pager{position:fixed;right:24px;bottom:18px;color:#fff8;font:500 14px/1 system-ui;letter-spacing:.1em}
</style>
</head>
<body>
<div id="stage">
  <section class="slide" data-title="封面">…</section>
  <section class="slide" data-title="应用场景">…</section>
  <!-- … -->
</div>
<div id="pager"></div>
<script src="libs/gsap/gsap.min.js"></script><!-- 按需,复制自 assets/lesson/libs/gsap/ -->
<script>
const slides=[...document.querySelectorAll('.slide')];
let cur=0, busy=false;

/* —— 等比缩放 —— */
function fit(){
  const s=Math.min(innerWidth/1920,innerHeight/1080);
  stage.style.transform=`translate(-50%,-50%) scale(${s})`;
}
addEventListener('resize',fit);fit();

/* —— 动效接线:slideenter ——
   原 scroll/click 驱动的配方统一改为「翻到该页时触发」。
   每页可选定义 window.enter[i](instant) —— instant=true 时直接落完工态。*/
const enterHooks={};
function show(i,instant){
  i=Math.max(0,Math.min(slides.length-1,i));
  slides[cur].classList.remove('on');
  cur=i; slides[cur].classList.add('on');
  location.hash=cur+1;
  pager.textContent=`${cur+1} / ${slides.length} · ${slides[cur].dataset.title||''}`;
  (enterHooks[cur]||noop)(instant);
}
const noop=()=>{};

/* —— 翻页控制 —— */
addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)) show(cur+1,e.repeat);
  if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)) show(cur-1,e.repeat);
  if(e.key==='Home') show(0); if(e.key==='End') show(slides.length-1);
});
/* 点击右半屏下一页、左半屏上一页(方便翻页笔/触屏) */
addEventListener('click',e=>{
  if(e.target.closest('a,button,input,[data-noflip]'))return;
  show(cur+(e.clientX>innerWidth/2?1:-1));
});

/* —— 启动:支持 #页码 直达(评委「翻到第 7 页」= 地址栏 #7)—— */
show((parseInt(location.hash.slice(1))||1)-1,true);
</script>
</body>
</html>
```

## 翻页瞬时性纪律(红线 2 的落地)

- **instant 模式**:`show(i,true)` 时跳过一切动画,直接写完工态;#hash 直达、Home/End、按住方向键连翻(e.repeat)都走 instant。
- **入场动效挂 enterHooks[i]**:用 GSAP timeline 或 vanilla 配方;每个 timeline 必须提供「立即完工」路径(`tl.progress(1)` 或不建 timeline 直接靠完工态 CSS)。
- 单动效 ≤1.2s,全页入场 ≤2.5s;播完常驻可见,JS 失效页面照样成立。
- **scroll 驱动配方不适用**(R0/P3-scrub/P5 Lenis):壳内无滚动。scroll 触发 → slideenter;scrub 进度 → 翻页即播完。
- R8 点击逐条:点击区域加 `data-noflip`,阻止冒泡误翻页;翻到下一页再翻回时保持已展开状态(幂等)。

## 库接线

- 建壳时从 `assets/lesson/libs/gsap/` 复制用到的文件进 `decks/<项目名>/libs/gsap/`(gsap.min.js 在前,插件同名 .min.js 在后),`<script>gsap.registerPlugin(...)</script>`。
- Lenis 不复制(无滚动场景)。插件按需,别整目录搬。
- 数字滚动(R4)等 vanilla 配方不需要 GSAP,能 vanilla 不 GSAP。

## 验收

playwright 逐页截图范式(参考 output/test/cn-lesson-shot.cjs 的逐卡单开思路):

```js
// 伪代码要点:1920×1080 viewport;逐页 #i 直达截图;收集 console error
for(let i=1;i<=N;i++){
  await page.goto(`file:///.../index.html#${i}`);
  await page.waitForTimeout(1800);          // 等入场播完
  await page.screenshot({path:`shots/${i}.png`});
}
// + 溢出检查:每页 evaluate 各 slide scrollHeight>1080 或 scrollWidth>1920 即报错
// + console error 收集,零报错才过
```

- 截图逐张人工过目:溢出、文字截断、图片缺失、风格漂移;
- 连翻测试:脚本 100ms 间隔连翻 10 页,截图末页应为完工态。
