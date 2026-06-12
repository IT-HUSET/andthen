/*
 * layout.mjs — collision-free auto-layout for the Architecture module map.
 *
 * Pure geometry, no HTML and no I/O: ranks → serpentine fold → rank slots →
 * edge attachment/routing → label placement → canvas extents. Every spatial
 * invariant (node fit, node overlap, edge clearance, label collisions) is
 * assertion-checked so a misrendered diagram fails the run instead of shipping.
 */

/* Font metrics are px-per-char estimates for ui-monospace at the emitted sizes
   (13px node name, 10px sub-label, 10.5px edge label). Boxes and label boxes
   are sized from these; the fit/overlap assertions keep the estimates honest. */
const TITLE_CHAR_PX = 7.8;
const SUB_CHAR_PX = 6.2;
const LABEL_CHAR_PX = 6.4;

const RANK_GAP = 175; /* horizontal gap between rank slots */
const V_GAP = 64;     /* vertical gap between nodes within a rank */
const ROW_GAP = 130;  /* vertical gap between serpentine rows */
const MARGIN = 48;

/* Chain-shaped graphs produce extreme aspect ratios that render unreadably
   small — fold the rank sequence into serpentine rows, but only when clearly
   too wide (> FOLD_WHEN_OVER), aiming for FOLD_TARGET. */
const FOLD_WHEN_OVER = 3.2;
const FOLD_TARGET = 2.4;

const EDGE_SLOT_SPREAD = 18; /* px between parallel attachments on one node side */
const SAMPLES = 80;          /* path sampling resolution for collision tests */
/* perpendicular control-point nudges, tried in order until a quadratic clears all nodes */
const CTRL_NUDGES = [60, -60, 110, -110, 170, -170, 240, -240, 320, -320, 420, -420];
const SIDE_FALLBACKS = [['R', 'L'], ['L', 'R'], ['B', 'T'], ['T', 'B'], ['R', 'T'], ['L', 'T'], ['R', 'B'], ['L', 'B'], ['B', 'L'], ['B', 'R'], ['T', 'L'], ['T', 'R']];
/* label anchor candidates: position along the edge (t) × perpendicular offset */
const LABEL_T_CANDIDATES = [0.5, 0.38, 0.62, 0.3, 0.7, 0.22, 0.78];
const LABEL_OFF_CANDIDATES = [16, -16, 28, -28, 42, -42, 58, -58, 76, -76];

export function layoutArchitecture(mapNodes, mapEdges, moduleChurn, nodeKey, assert) {
  const nodes = mapNodes.map((n, i) => {
    const w = Math.max(120, Math.ceil(Math.max(n.name.length * TITLE_CHAR_PX, (n.sub || '').length * SUB_CHAR_PX)) + 24);
    const h = n.sub ? 56 : 44;
    return { ...n, key: nodeKey(n), i, w, h };
  });
  nodes.forEach(n => {
    assert(n.w - 16 >= n.name.length * TITLE_CHAR_PX, 'node title does not fit box: ' + n.name);
    assert(n.w - 16 >= (n.sub || '').length * SUB_CHAR_PX, 'node sub-label does not fit box: ' + n.name);
  });
  const byKey = new Map(nodes.map(n => [n.key, n]));
  const edges = mapEdges.map((e, i) => {
    const fk = e.from.toLowerCase(), tk = e.to.toLowerCase();
    assert(byKey.has(fk), 'mapviz edge references unknown node "' + e.from + '"');
    assert(byKey.has(tk), 'mapviz edge references unknown node "' + e.to + '"');
    return { ...e, i, fk, tk };
  });
  /* ranks: longest path from sources, cycle-safe */
  const rank = {};
  nodes.forEach(n => { rank[n.key] = 0; });
  for (let it = 0; it <= nodes.length; it++) {
    let changed = false;
    edges.forEach(e => { if (rank[e.tk] < rank[e.fk] + 1) { rank[e.tk] = rank[e.fk] + 1; changed = true; } });
    if (!changed) break;
  }
  const maxRank = Math.max(...nodes.map(n => rank[n.key]));
  const ranks = [];
  for (let r = 0; r <= maxRank; r++) ranks.push(nodes.filter(n => rank[n.key] === r));
  const orderIdx = {};
  ranks.forEach((col, r) => {
    if (r > 0) {
      const bary = (n) => {
        const preds = edges.filter(e => e.tk === n.key).map(e => orderIdx[e.fk]).filter(v => v !== undefined);
        return preds.length ? preds.reduce((x, y) => x + y, 0) / preds.length : n.i;
      };
      col.sort((a, b) => { const d = bary(a) - bary(b); return d !== 0 ? d : a.i - b.i; });
    }
    col.forEach((n, j) => { orderIdx[n.key] = j; });
  });
  const rankW = ranks.map(col => Math.max(...col.map(n => n.w)));
  const colH = ranks.map(col => col.reduce((a, n) => a + n.h, 0) + (col.length - 1) * V_GAP);
  const R = ranks.length;
  function foldMetrics(K) {
    const rows = Math.ceil(R / K);
    const slots = Math.min(K, R);
    const slotW = Array(slots).fill(0);
    for (let r = 0; r < R; r++) {
      const row = Math.floor(r / K);
      let j = r - row * K;
      if (row % 2 === 1) j = K - 1 - j;
      slotW[j] = Math.max(slotW[j], rankW[r]);
    }
    const rowH = [];
    for (let i = 0; i < rows; i++) {
      let h = 0;
      for (let r = i * K; r < Math.min(R, (i + 1) * K); r++) h = Math.max(h, colH[r]);
      rowH.push(h);
    }
    const W = MARGIN * 2 + slotW.reduce((a, b) => a + b, 0) + (slots - 1) * RANK_GAP;
    const H = MARGIN * 2 + rowH.reduce((a, b) => a + b, 0) + (rows - 1) * ROW_GAP;
    return { K, rows, slotW, rowH, W, H, aspect: W / Math.max(1, H) };
  }
  let fold = foldMetrics(R);
  if (fold.aspect > FOLD_WHEN_OVER && R > 1) {
    let best = null;
    for (let K = R - 1; K >= 1; K--) {
      const cand = foldMetrics(K);
      if (cand.aspect <= FOLD_TARGET) { best = cand; break; }
      if (!best || Math.abs(cand.aspect - FOLD_TARGET) < Math.abs(best.aspect - FOLD_TARGET)) best = cand;
    }
    fold = best || fold;
  }
  const slotX = [MARGIN];
  for (let j = 1; j < fold.slotW.length; j++) slotX.push(slotX[j - 1] + fold.slotW[j - 1] + RANK_GAP);
  const rowY = [MARGIN];
  for (let i = 1; i < fold.rows; i++) rowY.push(rowY[i - 1] + fold.rowH[i - 1] + ROW_GAP);
  ranks.forEach((col, r) => {
    const row = Math.floor(r / fold.K);
    let j = r - row * fold.K;
    if (row % 2 === 1) j = fold.K - 1 - j;
    let y = rowY[row] + (fold.rowH[row] - colH[r]) / 2;
    col.forEach(n => { n.x = slotX[j] + (fold.slotW[j] - n.w) / 2; n.y = y; y += n.h + V_GAP; });
  });
  /* ring pads ∝ sqrt(module churn) */
  const maxModChurn = Math.max(...Object.values(moduleChurn), 0);
  const ringPad = (k, hot) => !hot ? 0
    : maxModChurn > 0 ? +(Math.min(8, Math.max(3, 3 + 5 * Math.sqrt((moduleChurn[k] || 0) / maxModChurn)))).toFixed(1) : 4;
  nodes.forEach(n => { n.pad = ringPad(n.key, n.hot); });
  /* node overlap assertion */
  const nrect = (n, inf) => ({ x: n.x - inf, y: n.y - inf, w: n.w + 2 * inf, h: n.h + 2 * inf });
  const overlap = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
  nodes.forEach((a, i) => nodes.slice(i + 1).forEach(b =>
    assert(!overlap(nrect(a, 8), nrect(b, 8)), 'nodes overlap: ' + a.name + ' / ' + b.name)));
  /* edge attach sides + slot spread */
  edges.forEach(e => {
    const f = byKey.get(e.fk), t = byKey.get(e.tk);
    const dxc = (t.x + t.w / 2) - (f.x + f.w / 2);
    const dyc = (t.y + t.h / 2) - (f.y + f.h / 2);
    if (Math.abs(dxc) >= Math.abs(dyc)) {
      if (dxc >= 0) { e.fSide = 'R'; e.tSide = 'L'; } else { e.fSide = 'L'; e.tSide = 'R'; }
    } else {
      if (dyc >= 0) { e.fSide = 'B'; e.tSide = 'T'; } else { e.fSide = 'T'; e.tSide = 'B'; }
    }
  });
  const slotGroups = new Map();
  edges.forEach(e => {
    [['f', e.fk, e.fSide, e.tk], ['t', e.tk, e.tSide, e.fk]].forEach(([end, key, side, otherKey]) => {
      const gk = key + '|' + side;
      if (!slotGroups.has(gk)) slotGroups.set(gk, []);
      slotGroups.get(gk).push({ e, end, other: byKey.get(otherKey) });
    });
  });
  slotGroups.forEach(group => {
    group.sort((a, b) => (a.other.y + a.other.x / 1e6) - (b.other.y + b.other.x / 1e6) || a.e.i - b.e.i);
    const k = group.length;
    group.forEach((g, j) => {
      const off = (j - (k - 1) / 2) * EDGE_SLOT_SPREAD;
      if (g.end === 'f') g.e.fOff = off; else g.e.tOff = off;
    });
  });
  const attach = (n, side, off) => {
    if (side === 'R') return [n.x + n.w, n.y + n.h / 2 + off];
    if (side === 'L') return [n.x, n.y + n.h / 2 + off];
    if (side === 'B') return [n.x + n.w / 2 + off, n.y + n.h];
    return [n.x + n.w / 2 + off, n.y];
  };
  /* edge routing: straight, else quadratic nudges to clear nodes */
  function quadPt(p1, c, p2, t) {
    const u = 1 - t;
    return [u * u * p1[0] + 2 * u * t * c[0] + t * t * p2[0], u * u * p1[1] + 2 * u * t * c[1] + t * t * p2[1]];
  }
  function samplePath(e) {
    const pts = [];
    for (let s = 0; s <= SAMPLES; s++) {
      const t = s / SAMPLES;
      pts.push(e.ctrl ? quadPt(e.p1, e.ctrl, e.p2, t)
        : [e.p1[0] + (e.p2[0] - e.p1[0]) * t, e.p1[1] + (e.p2[1] - e.p1[1]) * t]);
    }
    return pts;
  }
  const ptInRect = (p, r) => p[0] > r.x && p[0] < r.x + r.w && p[1] > r.y && p[1] < r.y + r.h;
  function pathClear(e) {
    const pts = samplePath(e);
    return nodes.every(n => {
      if (n.key === e.fk || n.key === e.tk) return true;
      const r = nrect(n, n.pad + 4);
      return !pts.some((p, i) => i > 2 && i < pts.length - 2 && ptInRect(p, r));
    });
  }
  function routeWith(e, fSide, tSide, fOff, tOff) {
    e.p1 = attach(byKey.get(e.fk), fSide, fOff);
    e.p2 = attach(byKey.get(e.tk), tSide, tOff);
    e.ctrl = null;
    if (pathClear(e)) return true;
    const mx = (e.p1[0] + e.p2[0]) / 2, my = (e.p1[1] + e.p2[1]) / 2;
    const dx = e.p2[0] - e.p1[0], dy = e.p2[1] - e.p1[1];
    const len = Math.max(1, Math.hypot(dx, dy));
    const px = -dy / len, py = dx / len;
    return CTRL_NUDGES.some(off => {
      e.ctrl = [mx + px * off, my + py * off];
      return pathClear(e);
    });
  }
  edges.forEach(e => {
    const routed = routeWith(e, e.fSide, e.tSide, e.fOff || 0, e.tOff || 0)
      || SIDE_FALLBACKS.some(([fs, ts]) => routeWith(e, fs, ts, 0, 0));
    assert(routed, 'could not route edge ' + e.from + ' -> ' + e.to + ' clear of nodes (tried all attachment sides)');
    assert(pathClear(e), 'edge ' + e.from + ' -> ' + e.to + ' crosses a node box');
    e.samples = samplePath(e);
  });
  /* edge label placement: nudge until collision-free vs nodes, labels, and all edge lines */
  const placed = [];
  const labelBox = (cx, cy, w) => ({ x: cx - w / 2, y: cy - 11, w, h: 14 });
  /* "removed" tags placed first so edge labels avoid them (collision-asserted) */
  nodes.filter(n => n.state === 'removed').forEach(n => {
    const w = 'removed'.length * LABEL_CHAR_PX + 6;
    const cands = [
      [n.x + n.w / 2, n.y - n.pad - 8],
      [n.x + n.w / 2, n.y + n.h + n.pad + 16],
      [n.x + n.w + n.pad + w / 2 + 10, n.y + n.h / 2 + 4],
      [n.x - n.pad - w / 2 - 10, n.y + n.h / 2 + 4]
    ];
    const ok = cands.some(([cx, cy]) => {
      const box = labelBox(cx, cy, w);
      if (box.x < 4 || box.y < 12) return false;
      if (nodes.some(n2 => n2 !== n && overlap(box, nrect(n2, n2.pad + 4)))) return false;
      const inflated = { x: box.x - 3, y: box.y - 3, w: box.w + 6, h: box.h + 6 };
      if (edges.some(e2 => e2.samples.some(pt => ptInRect(pt, inflated)))) return false;
      n.tagPos = [cx, cy];
      placed.push({ edge: { label: 'removed-tag ' + n.name }, box });
      return true;
    });
    assert(ok, 'could not place "removed" tag for node ' + n.name + ' without collisions');
  });
  edges.filter(e => e.label).forEach(e => {
    const w = e.label.length * LABEL_CHAR_PX;
    const cands = [];
    LABEL_T_CANDIDATES.forEach(t => {
      LABEL_OFF_CANDIDATES.forEach(off => cands.push([t, off]));
    });
    const ok = cands.some(([t, off]) => {
      const i = Math.round(t * SAMPLES);
      const p = e.samples[i], pn = e.samples[Math.min(SAMPLES, i + 1)];
      const dx = pn[0] - p[0], dy = pn[1] - p[1];
      const len = Math.max(1, Math.hypot(dx, dy));
      const cx = p[0] + (-dy / len) * off, cy = p[1] + (dx / len) * off;
      const box = labelBox(cx, cy, w);
      if (box.x < 4 || box.y < 12) return false;
      const hitNode = nodes.some(n => overlap(box, nrect(n, n.pad + 4)));
      if (hitNode) return false;
      const hitLabel = placed.some(pb => overlap({ x: box.x - 2, y: box.y - 2, w: box.w + 4, h: box.h + 4 }, pb.box));
      if (hitLabel) return false;
      const inflated = { x: box.x - 3, y: box.y - 3, w: box.w + 6, h: box.h + 6 };
      /* own edge excluded: on vertical (folded) edges a wide label can never clear its
         own line; the white paint-order halo keeps it readable over its own edge */
      const hitEdge = edges.some(e2 => e2 !== e && e2.samples.some(pt => ptInRect(pt, inflated)));
      if (hitEdge) return false;
      e.labelPos = [cx, cy];
      placed.push({ edge: e, box });
      return true;
    });
    assert(ok, 'could not place label for edge ' + e.from + ' -> ' + e.to + ' ("' + e.label + '") without collisions');
  });
  /* final collision re-verification (belt and braces) */
  placed.forEach(({ edge, box }) => {
    nodes.forEach(n => assert(!overlap(box, nrect(n, n.pad + 2)), 'label "' + edge.label + '" overlaps node ' + n.name));
    placed.forEach(other => {
      if (other.edge !== edge) assert(!overlap(box, other.box), 'labels overlap: "' + edge.label + '" / "' + other.edge.label + '"');
    });
  });
  /* canvas extents (grow as needed) */
  let W = 0, H = 0;
  nodes.forEach(n => { W = Math.max(W, n.x + n.w + n.pad); H = Math.max(H, n.y + n.h + n.pad); });
  placed.forEach(({ box }) => { W = Math.max(W, box.x + box.w); H = Math.max(H, box.y + box.h); });
  edges.forEach(e => e.samples.forEach(p => { W = Math.max(W, p[0]); H = Math.max(H, p[1]); }));
  return { nodes, edges, W: Math.ceil(W + MARGIN), H: Math.ceil(H + MARGIN), byKey, foldK: fold.K, foldRows: fold.rows };
}
