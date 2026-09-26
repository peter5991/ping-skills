#!/usr/bin/env node
/**
 * fetch-libs.mjs — 按 references/libs.md 的版本清单，把前端库下载到本地目录。
 *
 * 用法：
 *   node fetch-libs.mjs [目标目录] [库名...]
 *   node fetch-libs.mjs ./libs              # 全部
 *   node fetch-libs.mjs ./libs gsap lenis   # 指定库
 *
 * 要求 Node 18+（内置 fetch）。版本在此文件锁定，与 references/libs.md 保持一致；
 * 升级库时同时更新两处。文件路径通过 jsDelivr 的 npm 元数据 API 按后缀解析，
 * 避免因包内目录结构变化写死错误路径。
 */

import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const LIBS = [
  { name: 'gsap', pkg: 'gsap', version: '3.15.0', files: [
    { match: 'dist/gsap.min.js', out: 'gsap.min.js' },
    { match: 'dist/ScrollTrigger.min.js', out: 'ScrollTrigger.min.js' },
  ]},
  { name: 'three', pkg: 'three', version: '0.185.1', files: [
    { match: 'build/three.module.min.js', out: 'three.module.min.js' },
    { match: 'build/three.core.min.js', out: 'three.core.min.js' },
  ]},
  { name: 'echarts', pkg: 'echarts', version: '6.1.0', files: [
    { match: 'dist/echarts.min.js', out: 'echarts.min.js' },
  ]},
  { name: 'reveal', pkg: 'reveal.js', version: '6.0.1', files: [
    { match: 'dist/reveal.js', out: 'reveal.js' },
    { match: 'dist/reveal.css', out: 'reveal.css' },
    { match: 'dist/theme/black.css', out: 'reveal-theme-black.css' },
  ]},
  { name: 'lenis', pkg: 'lenis', version: '1.3.26', files: [
    { match: 'dist/lenis.min.js', out: 'lenis.min.js' },
  ]},
  { name: 'animejs', pkg: 'animejs', version: '4.5.0', files: [
    { match: 'dist/bundles/anime.umd.min.js', out: 'anime.min.js' },
  ]},
  { name: 'swiper', pkg: 'swiper', version: '14.2.0', files: [
    { match: 'swiper-bundle.min.js', out: 'swiper-bundle.min.js' },
    { match: 'swiper-bundle.min.css', out: 'swiper-bundle.min.css' },
  ]},
  { name: 'lottie', pkg: 'lottie-web', version: '5.13.0', files: [
    { match: 'build/player/lottie.min.js', out: 'lottie.min.js' },
  ]},
  { name: 'tsparticles', pkg: 'tsparticles', version: '4.4.0', files: [
    { match: 'tsparticles.bundle.min.js', out: 'tsparticles.bundle.min.js' },
  ]},
  { name: 'pixi', pkg: 'pixi.js', version: '8.20.1', files: [
    { match: 'dist/pixi.min.js', out: 'pixi.min.js' },
  ]},
  { name: 'rough', pkg: 'roughjs', version: '4.6.6', files: [
    { match: 'bundled/rough.js', out: 'rough.js' },
  ]},
  { name: 'tone', pkg: 'tone', version: '15.1.22', files: [
    { match: 'build/Tone.js', out: 'Tone.js' },
  ]},
];

const targetDir = path.resolve(process.argv[2] || './libs');
const filter = process.argv.slice(3).map(s => s.toLowerCase());
const selected = filter.length ? LIBS.filter(l => filter.includes(l.name)) : LIBS;

if (!selected.length) {
  console.error('没有匹配的库。可用：' + LIBS.map(l => l.name).join(', '));
  process.exit(1);
}

async function resolveFile(pkg, version, suffix) {
  const res = await fetch(`https://data.jsdelivr.com/v1/packages/npm/${pkg}@${version}?structure=flat`);
  if (!res.ok) throw new Error(`元数据请求失败 ${pkg}@${version}: HTTP ${res.status}`);
  const { files } = await res.json();
  const hit = files.find(f => f.name.endsWith('/' + suffix) || f.name === '/' + suffix);
  if (!hit) throw new Error(`在 ${pkg}@${version} 中找不到 *${suffix}，请检查 libs.md 并更新脚本`);
  return hit.name; // 形如 "/dist/gsap.min.js"
}

async function download(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`下载失败 ${url}: HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  if (buf.length < 100) throw new Error(`文件异常小（${buf.length}B），疑似错误响应: ${url}`);
  return buf;
}

await mkdir(targetDir, { recursive: true });
let failed = 0;

for (const lib of selected) {
  for (const f of lib.files) {
    try {
      const remotePath = await resolveFile(lib.pkg, lib.version, f.match);
      const url = `https://cdn.jsdelivr.net/npm/${lib.pkg}@${lib.version}${remotePath}`;
      const buf = await download(url);
      await writeFile(path.join(targetDir, f.out), buf);
      console.log(`✓ ${lib.name}@${lib.version}  ${f.out}  ${(buf.length / 1024).toFixed(0)} KB`);
    } catch (e) {
      failed++;
      console.error(`✗ ${lib.name}  ${f.out}  — ${e.message}`);
    }
  }
}

console.log(failed ? `\n完成，但有 ${failed} 个文件失败，请排查后重跑。` : `\n全部完成 → ${targetDir}`);
process.exit(failed ? 1 : 0);
