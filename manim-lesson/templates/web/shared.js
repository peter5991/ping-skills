// 交互页共用:SVG 工具、线性比例尺、拖拽、坐标轴、KaTeX、翻页键转发
// 课题相关的数学函数(如 fit/sse)写在各自的教具页里,不进共享层
const SVGNS = "http://www.w3.org/2000/svg";

function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (parent) parent.appendChild(e);
  return e;
}

function scale(d0, d1, r0, r1) {
  const f = (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
  f.inv = (p) => d0 + ((p - r0) / (r1 - r0)) * (d1 - d0);
  f.k = (r1 - r0) / (d1 - d0); // 每个数据单位对应多少像素(可为负)
  return f;
}

// 屏幕坐标 → SVG viewBox 坐标
function svgPoint(svg, evt) {
  const p = svg.createSVGPoint();
  p.x = evt.clientX; p.y = evt.clientY;
  return p.matrixTransform(svg.getScreenCTM().inverse());
}

// 拖拽:onMove 收到 SVG 坐标。
// 注意:被拖元素必须常驻 DOM、拖动中只更新属性——重建节点会丢掉 pointer capture(见 references/interactive.md)
function draggable(node, svg, onMove, onEnd) {
  node.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    node.setPointerCapture(e.pointerId);
    const move = (ev) => onMove(svgPoint(svg, ev), ev);
    const up = () => {
      node.removeEventListener("pointermove", move);
      node.removeEventListener("pointerup", up);
      node.removeEventListener("pointercancel", up);
      onEnd && onEnd();
    };
    node.addEventListener("pointermove", move);
    node.addEventListener("pointerup", up);
    node.addEventListener("pointercancel", up);
  });
}

function axes(g, sx, sy, xticks, yticks, fmtX = String, fmtY = String) {
  const a = el("g", { class: "axis" }, g);
  const [x0, x1] = [sx(xticks[0]), sx(xticks[xticks.length - 1])];
  const [y0, y1] = [sy(yticks[0]), sy(yticks[yticks.length - 1])];
  el("line", { x1: x0, y1: y0, x2: x1, y2: y0 }, a);
  el("line", { x1: x0, y1: y0, x2: x0, y2: y1 }, a);
  for (const t of xticks) {
    el("line", { x1: sx(t), y1: y0, x2: sx(t), y2: y0 + 5 }, a);
    el("text", { x: sx(t), y: y0 + 20, "text-anchor": "middle" }, a).textContent = fmtX(t);
  }
  for (const t of yticks) {
    el("line", { x1: x0 - 5, y1: sy(t), x2: x0, y2: sy(t) }, a);
    el("text", { x: x0 - 9, y: sy(t) + 4, "text-anchor": "end" }, a).textContent = fmtY(t);
  }
  return a;
}

function tex(node, s) {
  if (window.katex) katex.render(s, node, { throwOnError: false });
  else node.textContent = s;
}

// 嵌在 reveal.js 的 iframe 里时,键盘事件不会到达父页面 → 转发翻页键
(function forwardNav() {
  if (window.parent === window) return;
  window.addEventListener("keydown", (e) => {
    const next = ["ArrowRight", "ArrowDown", "PageDown", " "].includes(e.key);
    const prev = ["ArrowLeft", "ArrowUp", "PageUp"].includes(e.key);
    if (!next && !prev) return;
    if (e.target.closest && e.target.closest("input[type=range]")) return; // 滑块自己用方向键
    e.preventDefault();
    window.parent.postMessage({ type: "reveal-nav", dir: next ? "next" : "prev" }, "*");
  });
})();
