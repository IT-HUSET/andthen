#!/usr/bin/env node
/*
 * render-changeset.mjs — deterministic renderer for AndThen changeset-walkthrough artifacts.
 *
 * Usage: node render-changeset.mjs <artifact.md> <output.html>
 * Node >= 18, zero dependencies, zero external resources in the output.
 * Entry point of a sibling-file bundle shipped with the skill: layout.mjs
 * (module-map geometry), changeset.css, changeset-app.js, changeset-notes.js
 * (page assets, read at runtime and inlined into the single output HTML).
 *
 * Parses any artifact conforming to the changeset-walkthrough template contract:
 * H1 "Changeset Walkthrough:", TL;DR blockquote, At a Glance bold-key bullets,
 * Change Map table (File/Kind/Δ/Cluster/Risk/Role), Change Narrative H3 clusters
 * "C<N>: <title> – <kind>" (en or em dash), H4 file blocks, ```diff fences with
 * "@@ path:line @@" heads, blockquote margin notes, optional ## Architectural Delta
 * with a ```mapviz block, optional Reviewer Focus Points / Out of Scope / Verification.
 * Missing optional sections degrade gracefully. All layout math is computed here and
 * baked into the HTML; runtime JS is event wiring only.
 */
import fs from 'node:fs';
import crypto from 'node:crypto';
import { layoutArchitecture } from './layout.mjs';

const NUL = String.fromCharCode(0);

/* ===================== sibling assets (shipped with the skill) ===================== */
const readAsset = (name) => fs.readFileSync(new URL(name, import.meta.url), 'utf8');
const CSS = readAsset('changeset.css');
const APP_JS = readAsset('changeset-app.js');
const NOTES_JS = readAsset('changeset-notes.js');

/* ===================== cli ===================== */
const [, , srcArg, outArg] = process.argv;
if (!srcArg || !outArg) {
  console.error('usage: node render-changeset.mjs <artifact.md> <output.html>');
  process.exit(2);
}
const md = fs.readFileSync(srcArg, 'utf8');
const sha1 = crypto.createHash('sha1').update(srcArg).digest('hex');

let assertCount = 0;
const fail = (msg) => { throw new Error('render-changeset: ' + msg); };
const assert = (cond, msg) => { assertCount++; if (!cond) fail(msg); };
const at = (lineIdx) => ' (artifact line ' + (lineIdx + 1) + ')';

/* ===================== helpers ===================== */
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const kebab = (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
function mdInline(s) {
  const codes = [];
  let t = String(s).replace(/`([^`]+)`/g, (m, c) => { codes.push(c); return NUL + (codes.length - 1) + NUL; });
  t = esc(t);
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  t = t.replace(new RegExp(NUL + '(\\d+)' + NUL, 'g'), (m, i) => '<code>' + esc(codes[+i]) + '</code>');
  return t;
}
const stripMd = (s) => String(s).replace(/`/g, '').replace(/\*\*/g, '').replace(/(^|\s)\*([^*]+)\*/g, '$1$2');
function hslToHex(h, s, l) {
  const a = s * Math.min(l, 1 - l);
  const f = (n) => {
    const k = (n + h / 30) % 12;
    const c = l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1));
    return Math.round(255 * c).toString(16).padStart(2, '0');
  };
  return '#' + f(0) + f(8) + f(4);
}
const shortRef = (v) => {
  let t = String(v);
  if (/^[0-9a-f]{12,}$/i.test(t)) t = t.slice(0, 7);
  return t.length > 16 ? t.slice(0, 15) + '…' : t;
};
const KNOWN_RISK = ['attention', 'medium', 'safe'];
const riskClass = (r) => KNOWN_RISK.includes(r) ? 'r-' + r : 'r-neutral';

/* ===================== parse: sections ===================== */
const lines = md.split('\n');
const sectionStarts = [];
lines.forEach((l, i) => { if (l.startsWith('## ')) sectionStarts.push(i); });
const sections = {};
const sectionOrder = [];
sectionStarts.forEach((start, idx) => {
  const end = idx + 1 < sectionStarts.length ? sectionStarts[idx + 1] : lines.length;
  const heading = lines[start].slice(3).trim();
  sections[heading] = { heading, start, lines: lines.slice(start, end), raw: lines.slice(start, end).join('\n').trim() };
  sectionOrder.push(heading);
});
['At a Glance', 'Change Map', 'Change Narrative'].forEach(h =>
  assert(sections[h], 'required H2 section missing: "' + h + '"'));
const ordinalOf = (heading) => {
  const i = sectionOrder.indexOf(heading);
  assert(i >= 0, 'ordinal requested for unknown section ' + heading);
  return String(i + 1).padStart(2, '0');
};

const h1Idx = lines.findIndex(l => l.startsWith('# '));
assert(h1Idx >= 0, 'H1 heading missing');
const h1 = lines[h1Idx].slice(2).trim();
assert(/^Changeset Walkthrough/i.test(h1), 'H1 does not start with "Changeset Walkthrough"' + at(h1Idx));
const tldrIdx = lines.findIndex(l => l.startsWith('> TL;DR:'));
assert(tldrIdx >= 0, 'TL;DR blockquote missing');
const tldr = lines[tldrIdx].replace(/^> TL;DR:\s*/, '');

/* ===================== parse: At a Glance ===================== */
const glance = {};
sections['At a Glance'].lines.forEach(l => {
  const m = l.match(/^- \*\*([\w ]+)\*\*: (.*)$/);
  if (m) glance[m[1]] = m[2];
});
const statsLineIdx = sections['At a Glance'].lines.findIndex(l => l.includes('**Commits**'));
assert(statsLineIdx >= 0, 'At a Glance is missing the Commits/Files/Lines bullet' + at(sections['At a Glance'].start));
const stats = sections['At a Glance'].lines[statsLineIdx].match(/\*\*Commits\*\*: (\d+) · \*\*Files\*\*: (\d+) · \*\*Lines\*\*: \+(\d+) −(\d+)/);
assert(stats, 'Commits/Files/Lines bullet unparsed' + at(sections['At a Glance'].start + statsLineIdx));
const [, commits, fileTotal, linesAdd, linesDel] = stats;
const sourceSpans = [...(glance['Source'] || '').matchAll(/`([^`]+)`/g)].map(m => m[1]);
const releases = [...(glance['Source'] || '').matchAll(/release:\s*([\d.]+)/g)].map(m => m[1]);
const riskProfileWord = (glance['Risk profile'] || '').split(/ [–—] /)[0].trim().toLowerCase();

/* ===================== parse: Change Map ===================== */
const files = [];
sections['Change Map'].lines.forEach((l, li) => {
  if (!l.startsWith('| `')) return;
  const cells = l.split('|').map(c => c.trim());
  assert(cells.length >= 8, 'Change Map row has too few cells' + at(sections['Change Map'].start + li));
  const path = cells[1].replace(/`/g, '');
  const d = cells[3].match(/\+(\d+) −(\d+)/);
  assert(d, 'Change Map Δ cell unparsed for ' + path + at(sections['Change Map'].start + li));
  assert(/^C\d+$/.test(cells[4]), 'Change Map Cluster cell invalid for ' + path + at(sections['Change Map'].start + li));
  files.push({ path, kind: cells[2], adds: +d[1], dels: +d[2], cluster: cells[4], risk: cells[5], role: cells[6] });
});
assert(files.length > 0, 'Change Map table has no file rows');

/* noise groups + intro prose (both optional) */
const noiseGroups = [];
let noiseProseLine = '', changeMapIntro = '';
{
  const secLines = sections['Change Map'].lines;
  const noiseIdx = secLines.findIndex(l => l.startsWith('Skipped as noise'));
  if (noiseIdx > 0) {
    noiseProseLine = secLines[noiseIdx];
    for (let i = noiseIdx; i < secLines.length; i++) {
      const m = secLines[i].match(/^- \*\*(.+?) \((C[\d]+(?:[–—-]C[\d]+)?)\)\*\*: (.*)$/);
      if (m) {
        const countM = m[3].match(/^(~?)(\d+)\b/);
        noiseGroups.push({ label: m[1], clusterRef: m[2], body: m[3], count: countM ? countM[2] : null, approx: countM ? countM[1] === '~' : false });
      }
    }
  }
  changeMapIntro = secLines.slice(1, noiseIdx > 0 ? noiseIdx : secLines.length)
    .find(l => l.trim() && !l.startsWith('|') && !l.startsWith('- ')) || '';
}

/* ===================== parse: Change Narrative ===================== */
const clusters = [];
{
  const sec = sections['Change Narrative'];
  const nl = sec.lines;
  let cur = null, fileBlock = null, i = 1;
  const container = () => (fileBlock ? fileBlock.blocks : cur.introBlocks);
  while (i < nl.length) {
    const l = nl[i];
    const h3 = l.match(/^### (C\d+): (.+)$/);
    if (h3) {
      const rest = h3[2];
      const cut = Math.max(rest.lastIndexOf(' – '), rest.lastIndexOf(' — '));
      assert(cut > 0, 'cluster H3 missing " – <kind>" suffix: ' + l + at(sec.start + i));
      cur = { id: h3[1], n: +h3[1].slice(1), title: rest.slice(0, cut).trim(), kind: rest.slice(cut + 3).trim(), introBlocks: [], files: [] };
      clusters.push(cur); fileBlock = null; i++; continue;
    }
    if (!cur) { i++; continue; }
    const h4 = l.match(/^#### `(.+)`$/);
    if (h4) { fileBlock = { path: h4[1], blocks: [] }; cur.files.push(fileBlock); i++; continue; }
    if (l.startsWith('```diff')) {
      const fenceLine = i;
      const body = [];
      i++;
      while (i < nl.length && !nl[i].startsWith('```')) { body.push(nl[i]); i++; }
      i++;
      const head = (body[0] || '').match(/^@@ (.+?):(\d+) @@$/);
      assert(head, 'diff fence head must be "@@ path:line @@", got: ' + (body[0] || '(empty)') + at(sec.start + fenceLine + 1));
      container().push({ type: 'hunk', path: head[1], start: +head[2], lines: body.slice(1) });
      continue;
    }
    if (l.startsWith('> ')) {
      const quote = [];
      while (i < nl.length && nl[i].startsWith('> ')) { quote.push(nl[i].slice(2)); i++; }
      const blocks = container();
      const prev = blocks[blocks.length - 1];
      blocks.push({ type: (prev && prev.type === 'hunk') ? 'note' : 'quote', text: quote.join(' ') });
      continue;
    }
    if (l.trim() === '') { i++; continue; }
    const para = [];
    while (i < nl.length && nl[i].trim() !== '' && !nl[i].startsWith('#') && !nl[i].startsWith('```') && !nl[i].startsWith('> ')) {
      para.push(nl[i]); i++;
    }
    container().push({ type: 'p', text: para.join(' ') });
  }
}
assert(clusters.length > 0, 'Change Narrative has no "### C<N>: <title> – <kind>" clusters');
let hunkCount = 0, noteCount = 0;
clusters.forEach(c => c.files.forEach(f => f.blocks.forEach(b => { if (b.type === 'hunk') hunkCount++; if (b.type === 'note') noteCount++; })));

/* ===================== parse: optional sections ===================== */
let archProse = '', mapNodes = [], mapEdges = [], mapvizRaw = '';
const hasArch = !!sections['Architectural Delta'];
if (hasArch) {
  const sec = sections['Architectural Delta'];
  const al = sec.lines;
  const fenceStart = al.findIndex(l => l.startsWith('```mapviz'));
  if (fenceStart > 0) {
    archProse = al.slice(1, fenceStart).filter(l => l.trim()).join(' ');
    for (let i = fenceStart + 1; i < al.length && !al[i].startsWith('```'); i++) {
      const l = al[i].trim();
      if (!l) continue;
      let m = l.match(/^\[(\w+)\]\s+"([^"]*)"((?:\s+\w+)*)$/);
      if (m) {
        const flags = (m[3] || '').trim().split(/\s+/).filter(Boolean);
        mapNodes.push({ name: m[1], sub: m[2], hot: flags.includes('hot'), terminal: flags.includes('terminal'), chosen: flags.includes('chosen'), gate: false });
        continue;
      }
      m = l.match(/^\{(\w+):\s*(.*?)\}$/);
      if (m) { mapNodes.push({ name: m[1], sub: m[2], hot: false, terminal: false, chosen: false, gate: true }); continue; }
      m = l.match(/^(\w+)\s*(->|-\.->|=(\w+)=>)\s*(\w+)(?:\s*:\s*"(.*)")?$/);
      if (m) {
        const kind = m[2] === '-.->' ? 'async' : (m[3] === 'success' ? 'success' : m[3] === 'fail' ? 'fail' : '');
        mapEdges.push({ from: m[1], to: m[4], kind, label: m[5] || '' });
        continue;
      }
      fail('mapviz line unparsed: "' + l + '"' + at(sec.start + i));
    }
    mapvizRaw = al.slice(fenceStart, al.findIndex((l, j) => j > fenceStart && l.startsWith('```')) + 1).join('\n');
    assert(mapNodes.length > 0, 'mapviz block parsed to zero nodes' + at(sec.start + fenceStart));
  } else {
    archProse = al.slice(1).filter(l => l.trim()).join(' ');
  }
}
const hasMap = mapNodes.length > 0;
/* change-state derived purely from authored words (new/removed/changed/unchanged) */
mapNodes.forEach(n => {
  const segs = (n.sub || '').split('·').map(x => x.trim().toLowerCase());
  n.state = segs.includes('new') ? 'new' : segs.includes('removed') ? 'removed' : (n.hot ? 'changed' : 'unchanged');
});
mapEdges.forEach(e => {
  const w = ((e.label || '').split(' ')[0] || '').replace(/[^a-z]/g, '');
  e.state = ['new', 'changed', 'removed', 'unchanged'].includes(w) ? w : null;
});

const focus = [];
if (sections['Reviewer Focus Points']) {
  sections['Reviewer Focus Points'].lines.forEach(l => {
    const m = l.match(/^(\d+)\. \*\*(.+?)\*\* [–—] (.*) \(`(.+?):(\d+)`\)\.?$/);
    if (m) focus.push({ n: +m[1], title: m[2], desc: m[3], path: m[4], line: +m[5] });
  });
  assert(focus.length > 0, 'Reviewer Focus Points present but no numbered "**title** – desc (`path:line`)" items parsed');
}
const outOfScope = sections['Out of Scope']
  ? sections['Out of Scope'].lines.filter(l => l.startsWith('- ')).map(l => l.slice(2)) : [];
const verification = sections['Verification']
  ? sections['Verification'].lines.map(l => l.match(/^- \[( |x)\] (.*)$/)).filter(Boolean).map(m => ({ done: m[1] === 'x', text: m[2] })) : [];
if (sections['Out of Scope']) assert(outOfScope.length > 0, 'Out of Scope present but empty');
if (sections['Verification']) assert(verification.length > 0, 'Verification present but no checkbox items');

/* ===================== index + derived data ===================== */
const fileAnchor = (p) => 'change-narrative-' + kebab(p);
const stepAnchor = (n) => 'change-narrative-c' + n;
const h4Paths = new Set();
clusters.forEach(c => c.files.forEach(f => h4Paths.add(f.path)));
h4Paths.forEach(p => assert(files.some(f => f.path === p), 'narrative H4 file not in Change Map: ' + p));
const fileByPath = new Map(files.map(f => [f.path, f]));
const clusterById = new Map(clusters.map(c => [c.id, c]));
files.forEach(f => assert(clusterById.has(f.cluster), 'Change Map row references unknown cluster ' + f.cluster + ' (' + f.path + ')'));
const jumpFor = (path) => h4Paths.has(path) ? fileAnchor(path) : stepAnchor(fileByPath.get(path).cluster.slice(1));

clusters.forEach(c => {
  const rows = files.filter(f => f.cluster === c.id);
  assert(rows.length > 0, 'cluster ' + c.id + ' has no Change Map rows');
  c.fileCount = rows.length;
  c.adds = rows.reduce((a, r) => a + r.adds, 0);
  c.dels = rows.reduce((a, r) => a + r.dels, 0);
  c.churn = Math.max(1, c.adds + c.dels);
  c.fileChurns = rows.map(r => r.adds + r.dels);
});
const attentionCount = files.filter(f => f.risk === 'attention').length;
const riskCounts = {};
KNOWN_RISK.forEach(r => { riskCounts[r] = files.filter(f => f.risk === r).length; });
const kindOrder = [];
clusters.forEach(c => { if (!kindOrder.includes(c.kind)) kindOrder.push(c.kind); });
const kindCounts = {};
files.forEach(f => { const k = clusterById.get(f.cluster).kind; kindCounts[k] = (kindCounts[k] || 0) + 1; });

const hunkStats = new Map();
clusters.forEach(c => c.files.forEach(fb => {
  const hs = fb.blocks.filter(b => b.type === 'hunk').map(h => ({
    a: h.lines.filter(l => l.charAt(0) === '+').length,
    d: h.lines.filter(l => l.charAt(0) === '-').length
  }));
  if (hs.length) hunkStats.set(fb.path, hs);
}));
assert([...hunkStats.values()].reduce((a, v) => a + v.length, 0) === hunkCount, 'hunk stats out of sync with parsed hunks');

/* deterministic per-cluster hues, spread over a warm-anchored ramp */
const hues = {};
clusters.forEach((c, i) => {
  const deg = clusters.length === 1 ? 18 : 18 + i * (322 / (clusters.length - 1));
  hues['c' + c.n] = hslToHex(deg, 0.40, 0.50);
});
assert(Object.keys(hues).length === clusters.length, 'hue count must equal cluster count');
Object.values(hues).forEach(h => assert(/^#[0-9a-f]{6}$/.test(h), 'bad hue hex ' + h));

/* progress segments ∝ cluster churn */
const totalChurn = clusters.reduce((a, c) => a + c.churn, 0);
const segWidths = clusters.map(c => +(c.churn / totalChurn * 100).toFixed(2));
segWidths[segWidths.length - 1] = +(segWidths[segWidths.length - 1] + (100 - segWidths.reduce((a, b) => a + b, 0))).toFixed(2);
assert(Math.abs(segWidths.reduce((a, b) => a + b, 0) - 100) < 0.05, 'progress segment widths must sum to 100');

/* mosaic tile mini-bars: churn is encoded in the bar, never tile width (width reads as importance) */
const maxChurn = Math.max(...files.map(f => f.adds + f.dels), 1);
const barW = (v) => v > 0 ? Math.max(2, Math.round(34 * Math.sqrt(v / maxChurn))) : 0;
files.forEach(f => {
  assert(barW(f.adds) <= 34 && barW(f.dels) <= 34, 'tile mini-bar width out of bounds for ' + f.path);
});

/* ===================== generic cluster -> module mapping ===================== */
const nodeKey = (n) => n.name.toLowerCase();
function moduleFragments(node) {
  const frags = new Set();
  const snake = node.name.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toLowerCase();
  if (snake.length >= 4) frags.add(snake);
  if (node.name.length >= 4) frags.add(node.name.toLowerCase());
  const seg = (node.sub || '').split('·')[0].trim().toLowerCase();
  if (seg) {
    if (seg.includes('/') && !seg.includes(' ')) frags.add(seg);
    seg.split('/').map(t => t.trim()).forEach(t => { if (t.length >= 4 && !t.includes(' ')) frags.add(t); });
  }
  return [...frags];
}
const fragMatches = (frag, path) => {
  const p = path.toLowerCase();
  return frag.includes('/') ? frag.split('/').every(s => s && p.includes(s)) : p.includes(frag);
};
const fileModules = new Map();
const moduleChurn = {};
let clusterModules = {};
if (hasMap) {
  const genericCap = Math.max(5, Math.ceil(files.length * 0.25));
  mapNodes.forEach(n => {
    const k = nodeKey(n);
    moduleChurn[k] = 0;
    moduleFragments(n).forEach(frag => {
      const matches = files.filter(f => fragMatches(frag, f.path));
      if (matches.length === 0 || matches.length > genericCap) return; // too generic or useless
      matches.forEach(f => {
        if (!fileModules.has(f.path)) fileModules.set(f.path, new Set());
        fileModules.get(f.path).add(k);
      });
    });
  });
  files.forEach(f => (fileModules.get(f.path) || []).forEach(k => { moduleChurn[k] += f.adds + f.dels; }));
}
clusters.forEach(c => {
  const set = new Set();
  files.filter(f => f.cluster === c.id).forEach(f => (fileModules.get(f.path) || []).forEach(k => set.add(k)));
  clusterModules['c' + c.n] = [...set];
});
if (hasMap) {
  const nodeKeys = new Set(mapNodes.map(nodeKey));
  Object.values(clusterModules).forEach(list => list.forEach(k => assert(nodeKeys.has(k), 'derived module key not a map node: ' + k)));
}

/* blast sets (transitive dependents) + BFS depths from the most-churned hot node */
let blast = {}, bfs = [], bfsFrom = '';
if (hasMap) {
  const edgesK = mapEdges.map(e => ({ from: e.from.toLowerCase(), to: e.to.toLowerCase() }));
  mapNodes.forEach(n => {
    const k = nodeKey(n);
    const set = new Set();
    let grew = true;
    while (grew) {
      grew = false;
      edgesK.forEach(e => {
        if ((e.to === k || set.has(e.to)) && !set.has(e.from) && e.from !== k) { set.add(e.from); grew = true; }
      });
    }
    blast[k] = [...set];
  });
  const hotKeys = mapNodes.filter(n => n.hot).map(nodeKey);
  const pool = hotKeys.length ? hotKeys : mapNodes.map(nodeKey);
  bfsFrom = pool.reduce((a, b) => ((moduleChurn[a] || 0) >= (moduleChurn[b] || 0) ? a : b));
  const seen = new Set([bfsFrom]);
  let frontier = [bfsFrom];
  while (frontier.length) {
    bfs.push(frontier);
    const next = [];
    frontier.forEach(f => edgesK.forEach(e => { if (e.from === f && !seen.has(e.to)) { seen.add(e.to); next.push(e.to); } }));
    frontier = next;
  }
  const reach = new Set([bfsFrom]);
  let grew = true;
  while (grew) {
    grew = false;
    edgesK.forEach(e => { if (reach.has(e.from) && !reach.has(e.to)) { reach.add(e.to); grew = true; } });
  }
  assert(bfs.flat().length === reach.size, 'BFS depths must cover the forward-reachable set from ' + bfsFrom);
}

/* command palette index */
const palette = [];
clusters.forEach(c => palette.push({ t: 'cluster', n: c.n, label: c.id + ' · ' + stripMd(c.title), sub: c.fileCount + ' files · +' + c.adds + ' −' + c.dels }));
files.forEach(f => palette.push({ t: 'file', label: f.path, sub: f.cluster + ' · +' + f.adds + ' −' + f.dels, jump: jumpFor(f.path) }));
mapNodes.forEach(n => palette.push({ t: 'module', key: nodeKey(n), label: n.name, sub: n.sub }));
assert(palette.length === clusters.length + files.length + mapNodes.length, 'palette index size mismatch');

/* ===================== architecture data: detail panel, before/after, matrix ===================== */
const clusterModulesInverse = {};
Object.entries(clusterModules).forEach(([cid, keys]) => keys.forEach(k => {
  (clusterModulesInverse[k] = clusterModulesInverse[k] || []).push(cid);
}));
const moduleNames = {};
mapNodes.forEach(n => { moduleNames[nodeKey(n)] = n.name; });
const stChipCls = (st) => st === 'new' ? 'rk-new' : st === 'removed' ? 'rk-removed' : st === 'changed' ? 'rk-changed' : '';
const archDetailData = {};
const archEdgesData = mapEdges.map(e => ({
  fk: e.from.toLowerCase(), tk: e.to.toLowerCase(), fromName: e.from, toName: e.to,
  kind: e.kind, st: e.state, label: e.label
}));
if (hasMap) {
  const maxModuleChurn = Math.max(...Object.values(moduleChurn), 1);
  mapNodes.forEach(n => {
    const k = nodeKey(n);
    const dep = [...new Set(mapEdges.filter(e => e.from.toLowerCase() === k).map(e => e.to.toLowerCase()))];
    const use = [...new Set(mapEdges.filter(e => e.to.toLowerCase() === k).map(e => e.from.toLowerCase()))];
    const mapped = files.filter(f => (fileModules.get(f.path) || new Set()).has(k))
      .sort((a, b) => (b.adds + b.dels) - (a.adds + a.dels)).slice(0, 5)
      .map(f => ({ p: f.path, d: '+' + f.adds + ' −' + f.dels, j: jumpFor(f.path) }));
    const bl = blast[k] || [];
    archDetailData[k] = {
      t: n.name, m: n.sub || '', st: n.state,
      churn: moduleChurn[k] || 0,
      pct: Math.round(100 * (moduleChurn[k] || 0) / maxModuleChurn),
      by: clusterModulesInverse[k] || [], dep, use, files: mapped, blast: bl,
      b: (n.state === 'new' ? 'New in this changeset. ' : n.state === 'removed' ? 'Removed in this changeset. ' : n.state === 'changed' ? 'Changed in this changeset. ' : 'Unchanged. ')
        + (bl.length ? 'Changes here reach ' + bl.length + ' dependent module' + (bl.length === 1 ? '' : 's') + '.' : 'No modules depend on it.')
    };
  });
}
/* before/after toggle: only when authored new/removed states exist */
const baNames = (releases.length >= 2 ? [releases[1], releases[0]]
  : (sourceSpans.length >= 2 ? [sourceSpans[sourceSpans.length - 1], sourceSpans[0]] : ['Before', 'After'])).map(shortRef);
assert(baNames.every(n => n.length <= 16), 'structure-toggle labels must be capped at 16 chars');
const baCount = hasMap
  ? mapNodes.filter(n => n.state === 'new' || n.state === 'removed').length
    + mapEdges.filter(e => e.state === 'new' || e.state === 'removed').length
  : 0;
const baToggle = baCount > 0;
/* impact matrix: clusters × touched modules, capped at 12 columns by churn */
let imxHtml = '', imxDots = 0, imxCols = [];
if (hasMap) {
  const touched = [...new Set(Object.values(clusterModules).flat())];
  imxCols = touched.sort((a, b) => (moduleChurn[b] || 0) - (moduleChurn[a] || 0)).slice(0, 12);
  assert(imxCols.length <= 12, 'impact matrix capped at 12 columns');
  if (imxCols.length) {
    const cm = {};
    let maxCell = 1;
    clusters.forEach(c => {
      const cid = 'c' + c.n;
      cm[cid] = {};
      files.filter(f => f.cluster === c.id).forEach(f => (fileModules.get(f.path) || []).forEach(k => {
        if (imxCols.includes(k)) cm[cid][k] = (cm[cid][k] || 0) + Math.max(1, f.adds + f.dels);
      }));
      Object.values(cm[cid]).forEach(v => { maxCell = Math.max(maxCell, v); });
    });
    const out = ['<div class="imx-wrap"><table class="imx">'];
    out.push('<thead><tr><th></th>' + imxCols.map(k => '<th data-col="' + k + '"><span>' + esc(moduleNames[k] || k) + '</span></th>').join('') + '</tr></thead><tbody>');
    clusters.forEach(c => {
      const cid = 'c' + c.n;
      let title = stripMd(c.title);
      if (title.length > 40) title = title.slice(0, 39) + '…';
      out.push('<tr data-cluster="' + cid + '" style="--ch:' + hues[cid] + '"><th><span class="mg-dot"></span>' + esc(c.id + ' · ' + title) + '</th>'
        + imxCols.map(k => {
          const v = cm[cid][k];
          if (!v) return '<td data-col="' + k + '"></td>';
          imxDots++;
          const sz = v <= maxCell / 3 ? 's1' : v <= 2 * maxCell / 3 ? 's2' : 's3';
          return '<td data-col="' + k + '"><button type="button" class="imx-dot ' + sz + '" data-mk="' + k + '" data-step="' + c.n + '" style="--ch:' + hues[cid] + '"'
            + ' aria-label="' + esc(c.id + ' → ' + (moduleNames[k] || k)) + '" title="' + esc(c.id + ' → ' + (moduleNames[k] || k) + ' · ' + v + ' lines') + '"></button></td>';
        }).join('') + '</tr>');
    });
    out.push('</tbody></table></div>');
    imxHtml = out.join('\n');
    const expectedDots = clusters.reduce((a, c) => a + clusterModules['c' + c.n].filter(k => imxCols.includes(k)).length, 0);
    assert(imxDots === expectedDots, 'impact-matrix dot count ' + imxDots + ' != cluster→module mapping size ' + expectedDots);
  }
}

/* ===================== directory sunburst ===================== */
const RISK_FILL = { attention: '#D97757', medium: '#B89B6E', safe: '#788C5D' };
function dirOf(path) {
  const segs = path.split('/');
  return segs.length === 1 ? { top: '(root)', second: segs[0] } : { top: segs[0], second: segs[1] };
}
const sunTop = new Map();
files.forEach(f => {
  const { top, second } = dirOf(f.path);
  if (!sunTop.has(top)) sunTop.set(top, { churn: 0, adds: 0, dels: 0, files: 0, risk: {}, children: new Map() });
  const t = sunTop.get(top);
  const churn = Math.max(1, f.adds + f.dels);
  t.churn += churn; t.adds += f.adds; t.dels += f.dels; t.files++;
  t.risk[f.risk] = (t.risk[f.risk] || 0) + churn;
  if (!t.children.has(second)) t.children.set(second, { churn: 0, adds: 0, dels: 0, files: 0, risk: {} });
  const c2 = t.children.get(second);
  c2.churn += churn; c2.adds += f.adds; c2.dels += f.dels; c2.files++;
  c2.risk[f.risk] = (c2.risk[f.risk] || 0) + churn;
});
const domRisk = (riskMap) => {
  let best = null, bestV = -1;
  Object.entries(riskMap).forEach(([r, v]) => { if (v > bestV) { best = r; bestV = v; } });
  return RISK_FILL[best] || '#B8B5AC';
};
function arcPath(cx, cy, r0, r1, a0, a1) {
  if (a1 - a0 >= Math.PI * 2 - 1e-6) a1 = a0 + Math.PI * 2 - 1e-4;
  const px = (r, a) => (cx + r * Math.cos(a)).toFixed(2);
  const py = (r, a) => (cy + r * Math.sin(a)).toFixed(2);
  const large = (a1 - a0) > Math.PI ? 1 : 0;
  return 'M ' + px(r1, a0) + ' ' + py(r1, a0)
    + ' A ' + r1 + ' ' + r1 + ' 0 ' + large + ' 1 ' + px(r1, a1) + ' ' + py(r1, a1)
    + ' L ' + px(r0, a1) + ' ' + py(r0, a1)
    + ' A ' + r0 + ' ' + r0 + ' 0 ' + large + ' 0 ' + px(r0, a0) + ' ' + py(r0, a0) + ' Z';
}
function sunburstSvg() {
  const CX = 110, CY = 110, SZ = 220;
  const sunChurn = [...sunTop.values()].reduce((a, t) => a + t.churn, 0);
  const out = ['<svg class="sun" width="' + SZ + '" height="' + SZ + '" viewBox="0 0 ' + SZ + ' ' + SZ + '" role="img" aria-label="Directory churn sunburst">'];
  let a = -Math.PI / 2, total = 0;
  [...sunTop.entries()].forEach(([top, t]) => {
    const span = t.churn / sunChurn * Math.PI * 2;
    out.push('<path class="fseg has-tip" data-facet="dir" data-val="' + esc(top) + '"'
      + ' data-path="' + esc(top) + '/" data-delta="+' + t.adds + ' −' + t.dels + '" data-role="' + t.files + ' file' + (t.files === 1 ? '' : 's') + '"'
      + ' fill="' + domRisk(t.risk) + '" d="' + arcPath(CX, CY, 34, 62, a, a + span) + '"><title>' + esc(top) + '</title></path>');
    let a2 = a;
    [...t.children.entries()].forEach(([second, c2]) => {
      const span2 = c2.churn / sunChurn * Math.PI * 2;
      out.push('<path class="fseg has-tip" data-facet="dir" data-val="' + esc(top + '/' + second) + '"'
        + ' data-path="' + esc(top + '/' + second) + '" data-delta="+' + c2.adds + ' −' + c2.dels + '" data-role="' + c2.files + ' file' + (c2.files === 1 ? '' : 's') + '"'
        + ' fill="' + domRisk(c2.risk) + '" fill-opacity="0.62" d="' + arcPath(CX, CY, 66, 92, a2, a2 + span2) + '"><title>' + esc(top + '/' + second) + '</title></path>');
      a2 += span2;
    });
    assert(Math.abs(a2 - (a + span)) < 1e-6, 'sunburst child arcs of "' + top + '" must tile the parent arc');
    a += span; total += span;
  });
  assert(Math.abs(total - Math.PI * 2) < 1e-6, 'sunburst arcs must sum to a full circle');
  out.push('<text class="sc" x="' + CX + '" y="' + (CY - 2) + '">' + files.length + ' files</text>');
  out.push('<text class="sc" x="' + CX + '" y="' + (CY + 12) + '">' + sunTop.size + ' dirs</text>');
  out.push('</svg>');
  return out.join('\n');
}

/* ===================== architecture: module-map auto-layout (layout.mjs) ===================== */
const archLayout = hasMap ? layoutArchitecture(mapNodes, mapEdges, moduleChurn, nodeKey, assert) : null;

/* ===================== emit: hunks + blocks ===================== */
function renderHunk(h) {
  const out = [];
  out.push('<figure class="cw-hunk">');
  out.push('<figcaption class="cw-hunk-head"><code>' + esc(h.path + ':' + h.start) + '</code></figcaption>');
  out.push('<div class="cw-hunk-grid">');
  let ln = h.start;
  const rows = h.lines.length > 80 ? h.lines.slice(0, 60) : h.lines;
  rows.forEach(raw => {
    const mark = raw.charAt(0);
    const code = raw.slice(1);
    if (mark === '+') {
      out.push('<span class="ln l-add">' + (ln++) + '</span><span class="mk">+</span><code class="cd add">' + esc(code) + '</code>');
    } else if (mark === '-') {
      out.push('<span class="ln l-del"></span><span class="mk">−</span><code class="cd del">' + esc(code) + '</code>');
    } else {
      out.push('<span class="ln">' + (ln++) + '</span><span class="mk"> </span><code class="cd ctx">' + esc(code) + '</code>');
    }
  });
  if (h.lines.length > 80) {
    out.push('<span class="ln"></span><span class="mk"></span><code class="cd ctx">… hunk truncated for the tour – see the full diff in git/PR</code>');
  }
  out.push('</div></figure>');
  return out.join('\n');
}
function renderBlocks(blocks) {
  return blocks.map(b => {
    if (b.type === 'p') return '<p>' + mdInline(b.text) + '</p>';
    if (b.type === 'hunk') return renderHunk(b);
    if (b.type === 'note') return '<aside class="cw-hunk-note">' + mdInline(b.text) + '</aside>';
    if (b.type === 'quote') return '<blockquote>' + mdInline(b.text) + '</blockquote>';
    return '';
  }).join('\n');
}

/* ===================== emit: Section Block (notes-machinery contract) ===================== */
function sectionBlock(heading, bodyHtml, srcRaw, opts) {
  const anchor = kebab(heading);
  const o = opts || {};
  return [
    '<section class="card" id="' + anchor + '" data-anchor="' + anchor + '" data-heading="' + esc(heading) + '">',
    '<header class="card-head">',
    '<span class="h2-number">' + ordinalOf(heading) + '</span>',
    '<h2>' + esc(heading) + '</h2>',
    '<div class="card-actions">',
    '<button type="button" class="btn-note" data-act="note">+ Note <span class="note-count" data-role="count" data-empty="1">0</span></button>',
    '<button type="button" class="btn-source" data-act="src">View source</button>',
    '<button type="button" class="btn-copy-sect" data-act="copy-sect">Copy section</button>',
    '</div></header>',
    o.afterHead || '',
    '<div class="card-body">',
    bodyHtml,
    '</div>',
    '<div class="note-area" hidden>',
    '<textarea placeholder="Note for &quot;' + esc(heading) + '&quot;…" rows="3"></textarea>',
    '<div class="note-controls">',
    '<button type="button" class="btn-primary" data-add>Add note</button>',
    '<button type="button" data-cancel>Cancel</button>',
    '<span class="hint">⌘/Ctrl + Enter</span>',
    '</div>',
    '<ol class="note-list"></ol>',
    '</div>',
    '<pre class="src-area" hidden>' + esc(srcRaw) + '</pre>',
    '</section>'
  ].join('\n');
}

/* ===================== emit: Overview ===================== */
const basename = (p) => p.split('/').pop();
function noiseTile(g) {
  const label = g.count ? '+' + (g.approx ? '~' : '') + g.count + ' more' : 'more…';
  return '<span class="tile t-noise" title="' + esc(g.label + ' – ' + stripMd(g.body)) + '">' + esc(label) + '</span>';
}
function mosaic() {
  const out = ['<div class="mosaic">'];
  let ti = 0;
  clusters.forEach(c => {
    const cid = 'c' + c.n;
    out.push('<div class="mosaic-group">');
    out.push('<span class="mg-label" data-cluster="' + cid + '" style="--ch:' + hues[cid] + '"><span class="mg-dot"></span>' + esc(c.id + ' · ' + stripMd(c.title)) + '</span>');
    out.push('<div class="mg-tiles">');
    files.filter(f => f.cluster === c.id).forEach(f => {
      const hs = hunkStats.get(f.path);
      const hAttr = hs ? ' data-hunks="' + hs.map(x => x.a + '/' + x.d).join(',') + '"' : '';
      const label = basename(f.path);
      assert(label.length === basename(f.path).length, 'tile label must be the full basename: ' + f.path);
      const wa = barW(f.adds), wd = barW(f.dels);
      const bar = '<span class="tbar">'
        + (wa > 0 ? '<i class="ta" style="width:' + wa + 'px"></i>' : '')
        + (wd > 0 ? '<i class="td" style="width:' + wd + 'px"></i>' : '') + '</span>';
      out.push('<a class="tile ' + riskClass(f.risk) + ' settle has-tip" href="#" data-jump="' + jumpFor(f.path) + '"'
        + ' data-cluster="' + cid + '" data-path="' + esc(f.path) + '"'
        + ' data-delta="+' + f.adds + ' −' + f.dels + '" data-role="' + esc(stripMd(f.role)) + '"' + hAttr
        + ' style="--sd:' + Math.min(ti * 15, 900) + 'ms;--ch:' + hues[cid] + '">'
        + '<span>' + esc(label) + '</span>' + bar + '</a>');
      ti++;
    });
    noiseGroups.filter(g => g.clusterRef === c.id).forEach(g => out.push(noiseTile(g)));
    out.push('</div></div>');
  });
  const cross = noiseGroups.filter(g => /[–—-]/.test(g.clusterRef));
  if (cross.length) {
    out.push('<div class="mosaic-group">');
    out.push('<span class="mg-label">' + esc(cross.map(g => g.clusterRef + ' · ' + g.label + ' (skipped as noise)').join(' · ')) + '</span>');
    out.push('<div class="mg-tiles">');
    cross.forEach(g => out.push(noiseTile(g)));
    out.push('</div></div>');
  }
  out.push('</div>');
  return out.join('\n');
}
function firstSentence(c) {
  const text = c.introBlocks.filter(b => b.type === 'p').map(b => b.text).join(' ');
  const plain = stripMd(text);
  const parts = plain.split(/(?<=\.)\s+(?=[A-Z`])/);
  let s = parts[0] || plain;
  if (s.length < 40 && parts[1]) s += ' ' + parts[1];
  if (s.length > 240) s = s.slice(0, 237).replace(/\s+\S*$/, '') + '…';
  return s;
}
function sparkline(c) {
  const n = c.fileChurns.length;
  const maxC = Math.max(...c.fileChurns, 1);
  const pts = c.fileChurns.map((v, i) => {
    const x = n === 1 ? 60 : 4 + i * (112 / (n - 1));
    const y = 24 - (v / maxC) * 20;
    return x.toFixed(1) + ',' + y.toFixed(1);
  });
  assert(pts.length === c.fileCount, 'sparkline points != fileCount for ' + c.id);
  return '<svg class="spark" width="120" height="28" viewBox="0 0 120 28" aria-hidden="true">'
    + '<line class="base" x1="4" y1="24" x2="116" y2="24"/>'
    + '<polyline class="churn" pathLength="1" points="' + pts.join(' ') + '"/></svg>';
}
function clusterCards() {
  const out = ['<div class="cluster-grid">'];
  clusters.forEach(c => {
    const cid = 'c' + c.n;
    const aPct = Math.round(100 * c.adds / Math.max(1, c.adds + c.dels));
    out.push('<div class="cluster-card kind-' + kebab(c.kind) + '" data-cluster="' + cid + '" style="--ch:' + hues[cid] + '">');
    out.push('<div class="cc-head"><span class="cc-id">' + c.id + '</span><span class="cw-kind-chip kind-' + kebab(c.kind) + '">' + esc(c.kind) + '</span>'
      + '<span class="cc-stats">' + c.fileCount + ' files · <em class="add">+' + c.adds + '</em> <em class="del">−' + c.dels + '</em></span></div>');
    out.push('<div class="cc-title">' + esc(stripMd(c.title)) + '</div>');
    out.push('<p class="cc-desc">' + esc(firstSentence(c)) + '</p>');
    out.push('<div class="cc-bar" title="+' + c.adds + ' / −' + c.dels + '"><i class="a" style="width:' + aPct + '%"></i><i class="d" style="width:' + (100 - aPct) + '%"></i></div>');
    out.push('<div class="cc-foot"><a class="cc-walk" href="#" data-jump-step="' + c.n + '">Walk through →</a>' + sparkline(c) + '</div>');
    out.push('</div>');
  });
  out.push('</div>');
  return out.join('\n');
}
function focusRail() {
  const out = ['<div class="walk">'];
  focus.forEach(fp => {
    out.push('<div class="step"><div class="badge">' + fp.n + '</div><div class="step-body">');
    out.push('<div class="fp-title">' + mdInline(fp.title) + '</div>');
    out.push('<p class="fp-desc">' + mdInline(fp.desc) + '</p>');
    const target = fileByPath.has(fp.path) ? jumpFor(fp.path) : null;
    if (target) {
      out.push('<div class="step-loc"><a data-jump="' + target + '"><code>' + esc(fp.path + ':' + fp.line) + '</code></a></div>');
    } else {
      out.push('<div class="step-loc"><code>' + esc(fp.path + ':' + fp.line) + '</code></div>');
    }
    out.push('</div></div>');
  });
  out.push('</div>');
  return out.join('\n');
}
const atAGlanceBody = [
  '<div class="tldr"><span class="k">TL;DR</span><p class="v">' + mdInline(tldr) + '</p></div>',
  glance['Intent'] ? '<p class="intent-row"><span class="k">Intent</span><span class="v">' + mdInline(glance['Intent']) + '</span></p>' : ''
].join('\n');
const boundaryCards = [];
if (sections['Out of Scope']) {
  boundaryCards.push(sectionBlock('Out of Scope',
    '<p class="oos-eyebrow">deliberately not in this changeset</p><ul class="oos-list">'
    + outOfScope.map(b => '<li>' + mdInline(b) + '</li>').join('') + '</ul>',
    sections['Out of Scope'].raw));
}
if (sections['Verification']) {
  boundaryCards.push(sectionBlock('Verification',
    '<ul class="check-list">' + verification.map(v =>
      v.done
        ? '<li><span class="vbox"></span><span>' + mdInline(v.text) + '</span></li>'
        : '<li><span class="vbox open"></span><span>' + mdInline(v.text) + '<span class="chip-pending">pending</span></span></li>'
    ).join('') + '</ul>',
    sections['Verification'].raw));
}
const overviewHtml = [
  sectionBlock('At a Glance', atAGlanceBody, '> TL;DR: ' + tldr + '\n\n' + sections['At a Glance'].raw),
  '<div class="viz-block">',
  '<h2 class="viz-title">Change Mosaic</h2>',
  '<p class="viz-sub">all ' + files.length + ' mapped files · bar inside each tile = add/del churn (√ scale) · fill = risk (clay attention · oat medium · olive safe)'
  + (noiseGroups.length ? ' · dashed = skipped noise' : '') + ' · hover for detail, click to open in the tour</p>',
  mosaic(),
  '</div>',
  '<div class="viz-block">',
  '<h2 class="viz-title">Clusters</h2>',
  clusterCards(),
  '</div>',
  sections['Reviewer Focus Points']
    ? sectionBlock('Reviewer Focus Points',
        '<p class="viz-sub">start here – where careful reading pays off, in priority order</p>' + focusRail(),
        sections['Reviewer Focus Points'].raw)
    : '',
  boundaryCards.length ? '<div class="boundary-grid">' + boundaryCards.join('\n') + '</div>' : ''
].join('\n');

/* ===================== emit: Tour ===================== */
function fileSummary(f) {
  return '<summary><code class="cw-path">' + esc(f.path) + '</code>'
    + '<span class="cw-kind k-' + kebab(f.kind) + '">' + esc(f.kind) + '</span>'
    + '<span class="cw-delta"><em class="add">+' + f.adds + '</em> <em class="del">−' + f.dels + '</em></span>'
    + '<span class="cw-risk ' + riskClass(f.risk) + '">' + esc(f.risk) + '</span></summary>';
}
function tourSteps() {
  const out = [];
  clusters.forEach(c => {
    const cid = 'c' + c.n;
    out.push('<article class="tour-step" data-step="' + c.n + '" id="' + stepAnchor(c.n) + '" data-cluster="' + cid + '" style="--ch:' + hues[cid] + '">');
    out.push('<header class="ts-head"><span class="ts-id">' + c.id + '</span><h3>' + mdInline(c.title) + '</h3>');
    out.push('<span class="cw-kind-chip kind-' + kebab(c.kind) + '">' + esc(c.kind) + '</span>');
    out.push('<span class="ts-stats">' + c.fileCount + ' files · +' + c.adds + ' −' + c.dels + '</span>');
    out.push('<button class="btn-rev" data-rev="' + cid + '" type="button">'
      + '<svg class="rev-check" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5 6.5 12 13 4.5" fill="none" stroke="currentColor" stroke-width="2.2" pathLength="1"/></svg>'
      + '<span>Mark reviewed</span></button>');
    out.push('</header>');
    out.push(renderBlocks(c.introBlocks));
    c.files.forEach(fb => {
      const f = fileByPath.get(fb.path);
      const open = (f.risk === 'attention' || f.risk === 'medium') ? ' open' : '';
      out.push('<details class="cw-file" id="' + fileAnchor(fb.path) + '"' + open + '>');
      out.push(fileSummary(f));
      out.push('<div class="fb">' + renderBlocks(fb.blocks) + '</div>');
      out.push('</details>');
    });
    out.push('</article>');
  });
  return out.join('\n');
}
function miniMapSvg() {
  if (!archLayout) return '';
  const out = ['<svg class="mini-map" id="mini-map" viewBox="0 0 ' + archLayout.W + ' ' + archLayout.H + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Compact module map – click to expand">'];
  archLayout.edges.forEach(e => {
    const d = e.ctrl
      ? 'M ' + e.p1[0] + ' ' + e.p1[1] + ' Q ' + e.ctrl[0].toFixed(1) + ' ' + e.ctrl[1].toFixed(1) + ' ' + e.p2[0] + ' ' + e.p2[1]
      : 'M ' + e.p1[0] + ' ' + e.p1[1] + ' L ' + e.p2[0] + ' ' + e.p2[1];
    out.push('<path class="edge" d="' + d + '"/>');
  });
  archLayout.nodes.forEach(n => {
    const dc = (clusterModulesInverse[n.key] || []).length ? ' data-clusters="' + clusterModulesInverse[n.key].join(' ') + '"' : '';
    out.push('<rect class="mn" data-k="' + n.key + '"' + dc + ' x="' + n.x + '" y="' + n.y + '" width="' + n.w + '" height="' + n.h + '" rx="14"><title>' + esc(n.name) + '</title></rect>');
  });
  out.push('</svg>');
  return out.join('\n');
}
const tourNav = [
  '<nav class="tour-nav">',
  '<button class="tn-prev" type="button">← Prev</button>',
  '<ol class="tn-dots">',
  clusters.map(c => '<li data-step="' + c.n + '" data-cluster="c' + c.n + '" style="--ch:' + hues['c' + c.n] + '">' + c.id + '</li>').join(''),
  '</ol>',
  '<button class="tn-next" type="button">Next →</button>',
  '</nav>'
].join('\n');
const tourBody = [
  '<div class="tour-grid">',
  '<div class="tour-main">',
  '<div class="done-banner" id="done-banner" hidden>All ' + clusters.length + ' clusters reviewed · ' + fileTotal + ' files accounted for.</div>',
  tourSteps(),
  '</div>',
  '<div class="tour-rail">',
  '<div class="rail-card">',
  archLayout ? '<div class="rail-eyebrow">Modules touched by this cluster · click map to expand</div>' + miniMapSvg() + '<div class="rail-cap" id="rail-cap"></div>'
             : '<div class="rail-eyebrow">Review progress</div>',
  '<div class="film">',
  clusters.map(c => '<button class="fdot" type="button" data-step="' + c.n + '" data-cluster="c' + c.n + '" style="--ch:' + hues['c' + c.n] + '" aria-label="Go to ' + c.id + '">' + c.id + '</button>').join(''),
  '</div>',
  '</div>',
  '</div>',
  '</div>'
].join('\n');
const tourHtml = sectionBlock('Change Narrative', tourBody, sections['Change Narrative'].raw, { afterHead: tourNav });

/* ===================== emit: Files ===================== */
const maxRowValue = Math.max(...files.map(f => Math.max(f.adds, f.dels)), 1);
function filesView() {
  const out = [];
  if (changeMapIntro) out.push('<p>' + mdInline(changeMapIntro) + '</p>');
  out.push('<div class="files-top">');
  out.push('<div class="sun-card"><div class="sun-eyebrow">directory churn</div>' + sunburstSvg()
    + '<div class="sun-cap">inner = top-level dir · outer = second level · angle ∝ churn · fill = dominant risk · click to filter the table</div></div>');
  out.push('<div><div class="filter-bar">');
  out.push('<span class="fb-label">risk</span>');
  KNOWN_RISK.forEach(r => {
    out.push('<button class="fchip" data-facet="risk" data-val="' + r + '">' + r + ' <em>' + riskCounts[r] + '</em></button>');
  });
  out.push('<span class="fb-label">kind</span>');
  kindOrder.forEach(k => {
    out.push('<button class="fchip" data-facet="kind" data-val="' + esc(k) + '">' + esc(k) + ' <em>' + kindCounts[k] + '</em></button>');
  });
  out.push('<span class="fb-label">cluster</span>');
  clusters.forEach(c => {
    out.push('<button class="fchip" data-facet="cluster" data-val="c' + c.n + '" style="--ch:' + hues['c' + c.n] + '">' + c.id + ' <em>' + c.fileCount + '</em></button>');
  });
  out.push('<button class="fchip fb-clear" id="fb-clear" hidden>clear ×</button>');
  out.push('</div></div></div>');
  out.push('<table class="cw-filetable">');
  out.push('<thead><tr><th>File</th><th>Kind</th><th>Δ</th><th></th><th>Cluster</th><th>Risk</th><th>Role</th></tr></thead><tbody>');
  files.forEach(f => {
    const k = clusterById.get(f.cluster).kind;
    const cid = f.cluster.toLowerCase();
    const { top, second } = dirOf(f.path);
    const wa = Math.min(60, Math.round(60 * f.adds / maxRowValue));
    const wd = Math.min(60, Math.round(60 * f.dels / maxRowValue));
    const hs = hunkStats.get(f.path);
    let xray = '';
    if (hs) {
      xray = '<span class="xray">' + hs.map(x => {
        const a = '<i class="a" style="width:' + Math.max(3, Math.min(26, x.a * 2)) + 'px"></i>';
        const d = x.d > 0 ? '<i class="d" style="width:' + Math.max(2, Math.min(26, x.d * 2)) + 'px"></i>' : '';
        return a + d;
      }).join('') + '</span>';
    }
    out.push('<tr data-risk="' + esc(f.risk) + '" data-kind="' + esc(k) + '" data-cluster="' + cid + '"'
      + ' data-dir="' + esc(top) + '" data-dir2="' + esc(top + '/' + second) + '" style="--ch:' + hues[cid] + '">');
    out.push('<td><span class="copy-path" data-copy="' + esc(f.path) + '">' + esc(f.path) + '</span><span class="copy-flash">copied</span><a class="row-jump" data-jump="' + jumpFor(f.path) + '" title="open in tour">↗</a></td>');
    out.push('<td><span class="cw-kind k-' + kebab(f.kind) + '">' + esc(f.kind) + '</span></td>');
    out.push('<td class="delta">+' + f.adds + ' −' + f.dels + '</td>');
    out.push('<td class="dbar"><i class="da" style="width:' + wa + 'px"></i><i class="dd" style="width:' + wd + 'px"></i>' + xray + '</td>');
    out.push('<td><span class="cl-chip" style="--ch:' + hues[cid] + '">' + f.cluster + '</span></td>');
    out.push('<td><span class="cw-risk ' + riskClass(f.risk) + '">' + esc(f.risk) + '</span></td>');
    out.push('<td>' + mdInline(f.role) + '</td>');
    out.push('</tr>');
  });
  out.push('</tbody></table>');
  const noiseFileCount = +fileTotal - files.length;
  out.push('<p class="ft-count"><span id="ft-shown">' + files.length + '</span> of ' + files.length + ' mapped files'
    + (noiseGroups.length && noiseFileCount > 0
      ? ' · ' + noiseFileCount + ' more files summarized in ' + noiseGroups.length + ' <a href="#noise-groups">noise groups</a>' : '')
    + '</p>');
  if (noiseGroups.length) {
    out.push('<div class="noise-prose" id="noise-groups">');
    out.push('<p>' + mdInline(noiseProseLine) + '</p>');
    out.push('<ul>' + noiseGroups.map(g => '<li><strong>' + esc(g.label) + ' (' + esc(g.clusterRef) + ')</strong>: ' + mdInline(g.body) + '</li>').join('') + '</ul>');
    out.push('</div>');
  }
  return out.join('\n');
}
const filesHtml = sectionBlock('Change Map', filesView(), sections['Change Map'].raw);

/* ===================== emit: Architecture ===================== */
function moduleMapSvg() {
  const L = archLayout;
  const out = [];
  out.push('<svg class="diagram-module-map st-after" id="main-map" viewBox="0 0 ' + L.W + ' ' + L.H + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Module map for Architectural Delta">');
  out.push('<defs>'
    + '<marker id="arrow-gray" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#87867F"/></marker>'
    + '<marker id="arrow-clay" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#D97757"/></marker>'
    + '<marker id="arrow-olive" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#788C5D"/></marker>'
    + '<marker id="arrow-rust" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#B04A3F"/></marker>'
    + '</defs>');
  out.push('<g class="edges">');
  const markerFor = { '': 'arrow-gray', async: 'arrow-clay', success: 'arrow-olive', fail: 'arrow-rust' };
  L.edges.forEach(e => {
    const d = e.ctrl
      ? 'M ' + e.p1[0] + ' ' + e.p1[1] + ' Q ' + e.ctrl[0].toFixed(1) + ' ' + e.ctrl[1].toFixed(1) + ' ' + e.p2[0] + ' ' + e.p2[1]
      : 'M ' + e.p1[0] + ' ' + e.p1[1] + ' L ' + e.p2[0] + ' ' + e.p2[1];
    const stCls = e.state === 'new' ? ' is-new' : e.state === 'removed' ? ' is-removed' : '';
    out.push('<g class="eg' + stCls + '" data-e="' + e.i + '">');
    out.push('<path class="edge' + (e.kind ? ' ' + e.kind : '') + '" d="' + d + '" marker-end="url(#' + markerFor[e.kind] + ')"/>');
    if (e.label && e.labelPos) {
      out.push('<text class="elabel" x="' + e.labelPos[0].toFixed(1) + '" y="' + e.labelPos[1].toFixed(1) + '" text-anchor="middle">' + esc(e.label) + '</text>');
    }
    out.push('<path class="ehit" d="' + d + '"/>');
    out.push('</g>');
  });
  out.push('</g>');
  L.nodes.forEach(n => {
    const dc = (clusterModulesInverse[n.key] || []).length ? ' data-clusters="' + clusterModulesInverse[n.key].join(' ') + '"' : '';
    const stCls = n.state === 'new' ? ' is-new' : n.state === 'removed' ? ' is-removed' : '';
    const selCls = n.key === bfsFrom ? ' sel' : '';
    const classes = ['node', n.hot ? 'hot' : '', n.gate ? 'gate' : '', n.terminal ? 'term' : '', n.chosen ? 'chosen' : ''].filter(Boolean).join(' ') + stCls + selCls;
    out.push('<g class="' + classes + '" data-k="' + n.key + '"' + dc + '>');
    if (n.pad > 0) {
      out.push('<rect class="ring" x="' + (n.x - n.pad) + '" y="' + (n.y - n.pad) + '" width="' + (n.w + 2 * n.pad) + '" height="' + (n.h + 2 * n.pad) + '" rx="' + (6 + n.pad) + '"/>');
    }
    out.push('<rect class="bx" x="' + n.x + '" y="' + n.y + '" width="' + n.w + '" height="' + n.h + '" rx="' + (n.terminal ? 18 : 8) + '"/>');
    if (n.sub) {
      out.push('<text class="nm" x="' + (n.x + n.w / 2) + '" y="' + (n.y + 24) + '" text-anchor="middle">' + esc(n.name) + '</text>');
      out.push('<text class="sub" x="' + (n.x + n.w / 2) + '" y="' + (n.y + 41) + '" text-anchor="middle">' + esc(n.sub) + '</text>');
    } else {
      out.push('<text class="nm" x="' + (n.x + n.w / 2) + '" y="' + (n.y + n.h / 2 + 5) + '" text-anchor="middle">' + esc(n.name) + '</text>');
    }
    if (n.tagPos) {
      out.push('<text class="rm-tag" x="' + n.tagPos[0].toFixed(1) + '" y="' + n.tagPos[1].toFixed(1) + '">removed</text>');
    }
    out.push('</g>');
  });
  out.push('</svg>');
  return out.join('\n');
}
const relChip = (label) => {
  const kind = (label.split(' ')[0] || '').replace(/[^a-z]/g, '');
  const cls = { new: 'rk-new', changed: 'rk-changed', removed: 'rk-removed' }[kind] || '';
  return { kind: kind || 'edge', cls };
};
function zonesHtml(k) {
  const d = archDetailData[k];
  const linkBtns = (list) => list.length
    ? list.map(mk => '<button type="button" class="ad-link" data-selnode="' + mk + '">' + esc(moduleNames[mk] || mk) + '</button>').join('')
    : '<span class="ad-empty">—</span>';
  const out = [];
  out.push('<div class="ad-zone"><h4>mapped churn</h4><div class="ad-bar"><i style="width:' + d.pct + '%"></i></div><span class="ad-num">' + d.churn + ' lines across mapped files</span></div>');
  out.push('<div class="ad-zone"><h4>touched by</h4><div class="ad-chips">'
    + (d.by.length ? d.by.map(cid => '<button type="button" class="ad-chip" data-jump-step="' + cid.slice(1) + '" style="--ch:' + hues[cid] + '">' + cid.toUpperCase() + ' →</button>').join('')
      : '<span class="ad-empty">no mapped clusters</span>') + '</div></div>');
  out.push('<div class="ad-zone"><h4>depends on</h4><div class="ad-links">' + linkBtns(d.dep) + '</div></div>');
  out.push('<div class="ad-zone"><h4>used by</h4><div class="ad-links">' + linkBtns(d.use) + '</div></div>');
  if (d.files.length) {
    out.push('<div class="ad-zone"><h4>top files</h4><ul class="ad-files">'
      + d.files.map(f => '<li><a data-jump="' + f.j + '">' + esc(f.p) + '</a><span class="ad-d">' + esc(f.d) + '</span></li>').join('') + '</ul></div>');
  }
  out.push('<div class="ad-zone"><h4>blast radius</h4>'
    + (d.blast.length
      ? '<p class="ad-blast">changes here reach ' + d.blast.length + ' module' + (d.blast.length === 1 ? '' : 's') + ':</p><div class="ad-links">' + linkBtns(d.blast) + '</div>'
      : '<span class="ad-empty">no modules depend on it</span>') + '</div>');
  return out.join('\n');
}
function archView() {
  const out = [];
  if (archProse) out.push('<p>' + mdInline(archProse) + '</p>');
  if (!archLayout) return out.join('\n');
  out.push('<div class="arch-grid">');
  out.push('<div class="arch-left">');
  out.push('<div class="arch-tools"><button class="btn-ghost" id="play-flow" type="button">▶ Play flow</button>'
    + '<span class="blast-chip" id="blast-chip" hidden></span>'
    + (baToggle
      ? '<span class="ba-toggle" id="ba-toggle"><span class="fb-label">structure</span>'
        + '<button class="ba-seg" type="button" data-st="before" aria-pressed="false">' + esc(baNames[0]) + '</button>'
        + '<button class="ba-seg" type="button" data-st="after" aria-pressed="true">' + esc(baNames[1]) + '</button></span>'
      : '')
    + '<span class="diagram-caption">clay ring = changed, ring ∝ √churn · hover = blast radius · click node or edge = details · wheel/drag = zoom/pan</span></div>');
  out.push('<div class="map-wrap">');
  out.push('<div class="map-tools"><button id="zoom-in" type="button" aria-label="Zoom in">+</button><button id="zoom-out" type="button" aria-label="Zoom out">−</button><button id="zoom-reset" type="button" aria-label="Reset zoom">⌂</button></div>');
  out.push(moduleMapSvg());
  out.push('</div>');
  out.push('</div>');
  const dd = archDetailData[bfsFrom];
  out.push('<aside class="map-detail arch-detail" id="map-detail-architectural-delta">');
  out.push('<div class="hint">Click any node or edge in the map →</div>');
  out.push('<div class="ad-fade" id="ad-body">');
  out.push('<div class="ad-state"><span class="rel-chip ' + stChipCls(dd.st) + '" id="ad-chip">' + esc(dd.st) + '</span></div>');
  out.push('<h3 class="md-title" data-role="title">' + esc(dd.t) + '</h3>');
  out.push('<div class="md-meta" data-role="meta">' + esc(dd.m) + '</div>');
  out.push('<div class="md-body" data-role="body">' + esc(dd.b) + '</div>');
  out.push('<div class="ad-zones" id="ad-zones">' + zonesHtml(bfsFrom) + '</div>');
  out.push('</div>');
  out.push('</aside>');
  out.push('</div>');
  if (imxHtml) {
    out.push('<h3 class="rel-title">Impact matrix</h3>');
    out.push('<p class="viz-sub">clusters × modules · dot size = that cluster&#8217;s churn into the module (3 buckets) · hover highlights row/column · click a dot to inspect</p>');
    out.push(imxHtml);
  }
  const labeled = mapEdges.filter(e => e.label);
  if (labeled.length) {
    out.push('<h3 class="rel-title">Changed relationships</h3>');
    out.push('<ul class="rel-list">');
    labeled.forEach(e => {
      const c = relChip(e.label);
      const rest = e.label.includes('·') ? e.label.split('·').slice(1).join('·').trim() : (c.kind === 'unchanged' ? '' : e.label);
      out.push('<li><span class="rel-chip ' + c.cls + '">' + esc(c.kind) + '</span><code>' + esc(e.from) + '</code> → <code>' + esc(e.to) + '</code>'
        + (rest ? '<span class="rel-label">' + esc(rest) + '</span>' : '') + '</li>');
    });
    out.push('</ul>');
  }
  return out.join('\n');
}
const archHtml = hasArch ? sectionBlock('Architectural Delta', archView(), sections['Architectural Delta'].raw) : '';

/* ===================== baked runtime data ===================== */
/* archDetail ships only what the selection layer reads (st/t/m/b) plus the
   pre-rendered zone markup `z` — zonesHtml() is the single owner of that markup */
const archDetailBaked = Object.fromEntries(Object.keys(archDetailData).map((k) => {
  const d = archDetailData[k];
  return [k, { st: d.st, t: d.t, m: d.m, b: d.b, z: zonesHtml(k) }];
}));
const vxData = JSON.stringify({ sha: sha1, hues, clusterModules, moduleNames, blast, bfs, bfsFrom, palette, archDetail: archDetailBaked, archEdges: archEdgesData })
  .replace(/</g, NUL).split(NUL).join('\\u003c');

/* ===================== assemble page ===================== */
const jsEscape = (s) => String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
const notesJsFinal = NOTES_JS
  .replace('__ARTIFACT_PATH__', jsEscape(srcArg))
  .replace('__ARTIFACT_SHA1__', sha1);
const basenameSrc = srcArg.split('/').pop();
const riskPillClass = riskProfileWord ? ' risk-' + kebab(riskProfileWord) : '';
const headPills = [
  releases.length >= 2 ? '<span class="meta-pill"><span class="k">release</span> <span class="v">' + esc(releases[0] + ' vs ' + releases[1]) + '</span></span>' : '',
  sourceSpans.length >= 2 ? '<span class="meta-pill"><span class="k">diff</span> <span class="v">' + esc(shortRef(sourceSpans[0]) + ' → ' + shortRef(sourceSpans[1])) + '</span></span>' : '',
  '<span class="meta-pill"><span class="k">commits</span> <span class="v">' + commits + '</span></span>',
  riskProfileWord ? '<span class="meta-pill' + riskPillClass + '"><span class="k">risk</span> <span class="v">' + esc(riskProfileWord) + '</span></span>' : ''
].filter(Boolean).join('\n');

const html = [
  '<!DOCTYPE html>',
  '<html lang="en">',
  '<head>',
  '<meta charset="utf-8">',
  '<meta name="viewport" content="width=device-width, initial-scale=1">',
  '<title>' + esc(h1) + '</title>',
  '<style>',
  CSS,
  '</style>',
  '</head>',
  '<body>',
  '<div class="progress" id="progress" aria-hidden="true">',
  clusters.map((c, i) => '<div class="pseg" data-step="' + c.n + '" data-cluster="c' + c.n + '" style="width:' + segWidths[i] + '%;--ch:' + hues['c' + c.n] + '" title="' + esc(c.id + ' · ' + stripMd(c.title)) + '"><i class="pfill"></i></div>').join(''),
  '</div>',
  '<header class="topbar"><div class="tb-inner">',
  '<div class="tb-row">',
  '<span class="crumb">andthen:visualize · changeset · ' + esc(basenameSrc) + '</span>',
  '<div class="tb-actions">',
  '<button class="btn-ghost" id="open-cmdk-hint" type="button" onclick="document.dispatchEvent(new KeyboardEvent(\'keydown\',{key:\'k\',metaKey:true}))"><kbd class="khint">⌘K</kbd> Jump</button>',
  '<button class="btn-notes" id="notes-toggle" type="button">Notes <span class="note-total">0</span></button>',
  '<button class="btn-primary" id="copy-notes" type="button" disabled>Copy notes</button>',
  '</div></div>',
  '<div class="tb-row tb-title">',
  '<h1>' + esc(h1) + '</h1>',
  '<span class="inline-stats">' + fileTotal + ' files · <span class="add">+' + linesAdd + '</span> <span class="del">−' + linesDel + '</span> · ' + clusters.length + ' clusters</span>',
  '<div class="meta-pills">',
  headPills,
  '</div></div>',
  '<div class="kpi-strip">',
  '<div class="kpi"><span class="k">Files</span><span class="v"><em class="cnt" data-n="' + fileTotal + '">' + fileTotal + '</em></span></div>',
  '<div class="kpi"><span class="k">Lines Δ</span><span class="v"><em class="add">+<em class="cnt" data-n="' + linesAdd + '">' + linesAdd + '</em></em> <em class="del">−<em class="cnt" data-n="' + linesDel + '">' + linesDel + '</em></em></span></div>',
  '<div class="kpi"><span class="k">Clusters</span><span class="v"><em class="cnt" data-n="' + clusters.length + '">' + clusters.length + '</em></span></div>',
  '<div class="kpi' + (attentionCount > 0 ? ' attention' : '') + '"><span class="k">Attention</span><span class="v"><em class="cnt" data-n="' + attentionCount + '">' + attentionCount + '</em></span></div>',
  '</div>',
  '<nav class="view-tabs" role="tablist">',
  '<button class="view-tab" role="tab" data-view="overview" aria-selected="true">Overview</button>',
  '<button class="view-tab" role="tab" data-view="tour" aria-selected="false">Tour <span class="tab-hint">' + clusters.length + '</span></button>',
  '<button class="view-tab" role="tab" data-view="files" aria-selected="false">Files <span class="tab-hint">' + files.length + '</span></button>',
  hasArch ? '<button class="view-tab" role="tab" data-view="arch" aria-selected="false">Architecture</button>' : '',
  '</nav>',
  '</div></header>',
  '<main class="views">',
  '<div class="view" data-view="overview">', overviewHtml, '</div>',
  '<div class="view" data-view="tour">', tourHtml, '</div>',
  '<div class="view" data-view="files">', filesHtml, '</div>',
  hasArch ? '<div class="view" data-view="arch">\n' + archHtml + '\n</div>' : '',
  '</main>',
  '<aside class="notes-drawer" id="notes-drawer" hidden>',
  '<h2 class="nd-title">Notes</h2>',
  '<ol class="note-list"></ol>',
  '<p class="nd-hint">Add notes via the + Note button on any section, then Copy notes.</p>',
  '</aside>',
  '<div class="tip" id="tip" hidden></div>',
  '<div class="lightbox" id="lightbox" hidden role="dialog" aria-label="Module map"><div class="lb-card"></div></div>',
  '<div class="imx-pop" id="imx-pop" hidden></div>',
  '<div class="cmdk" id="cmdk" hidden role="dialog" aria-label="Jump to">',
  '<div class="cmdk-panel">',
  '<input id="cmdk-in" type="text" placeholder="Jump to cluster, file' + (hasMap ? ', or module' : '') + '…" autocomplete="off" spellcheck="false">',
  '<ol class="cmdk-list" id="cmdk-list"></ol>',
  '<div class="cmdk-hint">↑↓ navigate · ↵ jump · esc close</div>',
  '</div></div>',
  '<div class="keys-pop" id="keys-pop" hidden>',
  '<h3>Keyboard</h3>',
  '<table>',
  '<tr><td><kbd>⌘/Ctrl K</kbd></td><td>command palette</td></tr>',
  '<tr><td><kbd>←</kbd> <kbd>→</kbd></td><td>prev / next cluster</td></tr>',
  '<tr><td><kbd>j</kbd> <kbd>k</kbd></td><td>next / prev file block</td></tr>',
  '<tr><td><kbd>?</kbd></td><td>toggle this panel</td></tr>',
  '<tr><td><kbd>esc</kbd></td><td>close overlays</td></tr>',
  '</table></div>',
  '<script type="application/json" id="vx-data">' + vxData + '</' + 'script>',
  '<script>',
  APP_JS,
  '</' + 'script>',
  '<script>',
  notesJsFinal,
  '</' + 'script>',
  '</body>',
  '</html>'
].join('\n');

/* ===================== output validation ===================== */
const ids = new Set();
for (const m of html.matchAll(/ id="([^"]+)"/g)) ids.add(m[1]);
const jumps = [...html.matchAll(/data-jump="([^"]+)"/g)].map(m => m[1]);
jumps.forEach(j => assert(ids.has(j), 'data-jump target missing from output: ' + j));
const jumpSteps = [...html.matchAll(/data-jump-step="(\d+)"/g)].map(m => +m[1]);
jumpSteps.forEach(s => assert(s >= 1 && s <= clusters.length, 'data-jump-step out of range: ' + s));
for (const m of html.matchAll(/href="#([^"]+)"/g)) {
  if (m[1] === '') continue;
  assert(ids.has(m[1]), 'href anchor missing from output: ' + m[1]);
}
const validCids = new Set(clusters.map(c => 'c' + c.n));
for (const m of html.matchAll(/data-cluster="([^"]+)"/g)) assert(validCids.has(m[1]), 'bad data-cluster value: ' + m[1]);
for (const m of html.matchAll(/data-clusters="([^"]+)"/g)) m[1].split(' ').forEach(c => assert(validCids.has(c), 'bad data-clusters value: ' + c));
const counts = {
  tiles: (html.match(/class="tile /g) || []).length,
  filterChips: (html.match(/class="fchip" data-facet/g) || []).length,
  tourSteps: (html.match(/class="tour-step"/g) || []).length,
  hunks: (html.match(/class="cw-hunk"/g) || []).length,
  marginNotes: (html.match(/class="cw-hunk-note"/g) || []).length,
  filmDots: (html.match(/class="fdot"/g) || []).length,
  progressSegments: (html.match(/class="pseg"/g) || []).length,
  sparklines: (html.match(/class="spark"/g) || []).length,
  reviewButtons: (html.match(/class="btn-rev"/g) || []).length,
  sunArcs: (html.match(/class="fseg has-tip"/g) || []).length,
  counters: (html.match(/class="cnt"/g) || []).length,
  dataJumpLinks: jumps.length,
  uniqueJumpTargets: new Set(jumps).size
};
assert(counts.tourSteps === clusters.length, 'tour steps emitted: ' + counts.tourSteps);
assert(counts.hunks === hunkCount, 'hunk figures emitted: ' + counts.hunks + ' vs parsed ' + hunkCount);
assert(counts.marginNotes === noteCount, 'margin notes emitted: ' + counts.marginNotes + ' vs parsed ' + noteCount);
assert(counts.tiles === files.length + noiseGroups.length, 'tiles emitted: ' + counts.tiles);
assert(counts.filterChips === KNOWN_RISK.length + kindOrder.length + clusters.length, 'filter chips emitted: ' + counts.filterChips);
assert(counts.filmDots === clusters.length && counts.progressSegments === clusters.length
  && counts.sparklines === clusters.length && counts.reviewButtons === clusters.length, 'per-cluster widgets must equal cluster count');
assert(counts.sunArcs >= sunTop.size, 'sunburst arcs emitted: ' + counts.sunArcs);
assert(counts.counters === 5, 'expected 5 KPI counters, got ' + counts.counters);
if (archLayout) {
  assert((html.match(/class="ring"/g) || []).length === archLayout.nodes.filter(n => n.pad > 0).length, 'one ring per hot node');
}
assert(html.indexOf(NUL) === -1, 'NUL bytes leaked into the output');
/* sibling assets are inlined verbatim into <style>/<script> blocks — a literal close tag would truncate the page */
assert(!CSS.includes('</' + 'style>'), 'changeset.css must not contain a literal style close tag');
[['changeset-app.js', APP_JS], ['changeset-notes.js', notesJsFinal]].forEach(([name, s]) =>
  assert(!s.includes('</' + 'script>'), name + ' must not contain a literal script close tag'));
assert(/\.pseg\.lit\s*\{[^}]*box-shadow:\s*none[^}]*brightness\(/.test(CSS), 'progress segments must highlight by brightness only — outline treatment reads as noise on 3px segments');
/* behavior self-test: the node/edge click path must be intact (pointer capture regression) */
{
  const pdIdx = APP_JS.indexOf("addEventListener('pointerdown'");
  assert(pdIdx >= 0, 'zoom wiring must register a pointerdown handler');
  const pdBody = APP_JS.slice(pdIdx, APP_JS.indexOf('addEventListener', pdIdx + 30));
  assert(!pdBody.includes('setPointerCapture'), 'pointerdown must NOT capture the pointer (capture retargets clicks to the svg root and kills selection)');
  assert(APP_JS.includes('Math.abs(dx)<4&&Math.abs(dy)<4'), 'pan must start only after a 4px movement threshold');
  assert(APP_JS.includes('suppressClick'), 'pan release must suppress exactly one click');
  assert(APP_JS.includes("getElementById('main-map')") && APP_JS.includes("selMap.addEventListener('click'"), 'selection delegate must bind #main-map');
}
assert(/\.diagram-module-map \.ring[^}]*pointer-events: none/.test(CSS), 'decorative rings must be pointer-transparent (they sit over nodes and cause hover flicker loops)');
assert(/\.diagram-module-map text \{[^}]*pointer-events: none/.test(CSS), 'svg text decorations must be pointer-transparent (they intercept node clicks)');
if (hasMap) {
  const mmStart = html.indexOf('id="main-map"');
  const mmSvg = html.slice(mmStart, html.indexOf('</svg>', mmStart));
  const svgKeys = [...mmSvg.matchAll(/<g class="node[^"]*" data-k="([^"]+)"/g)].map(m => m[1]);
  assert(svgKeys.length === mapNodes.length, 'every map node must be an interactive g.node[data-k] inside #main-map (got ' + svgKeys.length + ')');
  svgKeys.forEach(k => assert(archDetailData[k], 'archDetail dictionary missing key for clickable node: ' + k));
}
if (hasMap) {
  assert(html.includes('<h3 class="md-title" data-role="title">' + esc(archDetailData[bfsFrom].t)),
    'detail panel must pre-select the most-churned node ' + bfsFrom);
  assert((html.match(/class="node[^"]*\bsel\b[^"]*"/g) || []).length === 1, 'exactly one node must be pre-selected');
  Object.keys(archDetailBaked).forEach(k =>
    assert(archDetailBaked[k].z.includes('ad-zone'), 'baked zone markup missing for node ' + k));
  assert(html.includes('id="ad-zones"'), 'detail panel zones must be baked (panel never empty)');
  const newCount = mapNodes.filter(n => n.state === 'new').length + mapEdges.filter(e => e.state === 'new').length;
  const remCount = mapNodes.filter(n => n.state === 'removed').length + mapEdges.filter(e => e.state === 'removed').length;
  assert((html.match(/class="[^"]*\bis-new\b/g) || []).length === newCount, 'is-new element count must equal authored "new" labels (' + newCount + ')');
  assert((html.match(/class="[^"]*\bis-removed\b/g) || []).length === remCount, 'is-removed element count must equal authored "removed" labels (' + remCount + ')');
  assert(html.includes('class="ba-toggle"') === (newCount + remCount > 0), 'before/after toggle present iff authored new/removed states exist');
  assert((html.match(/class="rm-tag"/g) || []).length === mapNodes.filter(n => n.state === 'removed').length, 'one removed-tag per removed node');
  assert((html.match(/class="ehit"/g) || []).length === mapEdges.length, 'one selectable hit-path per edge');
  const nodeKeysSet = new Set(mapNodes.map(nodeKey));
  for (const m of html.matchAll(/data-selnode="([^"]+)"/g)) assert(nodeKeysSet.has(m[1]), 'data-selnode references unknown module: ' + m[1]);
  for (const m of html.matchAll(/data-mk="([^"]+)"/g)) assert(nodeKeysSet.has(m[1]), 'data-mk references unknown module: ' + m[1]);
  assert((html.match(/class="imx-dot /g) || []).length === imxDots, 'emitted matrix dots must equal computed mapping cells');
} else {
  assert(!html.includes('class="ba-toggle"') && !html.includes('class="imx-wrap"') && !html.includes('id="ad-zones"'),
    'no-architecture artifacts must omit toggle, matrix, and detail panel');
}
assert(!/src="http|href="http|url\(http|@import/.test(html), 'external resources are forbidden');

fs.writeFileSync(outArg, html);
console.log('written: ' + outArg);
console.log(JSON.stringify({ bytes: html.length, assertions: assertCount, files: files.length, clusters: clusters.length, hasArch, hasMap, archCanvas: archLayout ? archLayout.W + 'x' + archLayout.H : null, fold: archLayout ? archLayout.foldK + 'K/' + archLayout.foldRows + 'rows' : null, bfsFrom: bfsFrom || null, baToggle, imxDots, imxCols: imxCols.length, ...counts }, null, 1));
