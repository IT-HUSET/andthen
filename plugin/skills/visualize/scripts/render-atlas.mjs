#!/usr/bin/env node
/*
 * render-atlas.mjs – deterministic renderer for AndThen atlas model artifacts
 * (architecture-model.json / domain-model.json, branched on `kind`).
 *
 * Usage: node render-atlas.mjs <model.json> <output.html>
 * Node >= 18, zero dependencies, zero external resources in the output.
 *
 * Validates the model structurally – the checks are identical to
 * scripts/validate-architecture-model.sh (agreed parity checklist; keep
 * both in sync) – then injects it into templates/atlas.html at the
 * __ATLAS_MODEL__ slot and bakes the SHA-256 hash of the single inline
 * script into the page CSP. Identical input bytes produce identical
 * output bytes: no nonces, no timestamps, no randomness.
 * Exit codes: 0 rendered · 1 model validation failed (artifact's fault)
 * · 2 usage or renderer/template defect (not the artifact's fault).
 */
import fs from 'node:fs';
import crypto from 'node:crypto';

const [, , srcArg, outArg] = process.argv;
if (!srcArg || !outArg) {
  console.error('usage: node render-atlas.mjs <model.json> <output.html>');
  process.exit(2);
}

let raw;
try {
  raw = fs.readFileSync(srcArg, 'utf8');
} catch (e) {
  console.error('render-atlas: cannot read ' + srcArg + ': ' + e.message);
  process.exit(2);
}

/* ===================== structural validation ===================== */
const errors = [];
const err = (msg) => errors.push(msg);
/* whitespace-only strings are as unusable as empty ones – parity with the
   shell validator's strip() semantics */
const isStr = (v) => typeof v === 'string' && v.trim().length > 0;
const isOptStr = (v) => v === undefined || typeof v === 'string';
const isNonNegInt = (v) => Number.isInteger(v) && v >= 0;

const CTX_KINDS = ['bounded-context', 'layer', 'subsystem', 'external'];
const METRIC_KEYS = ['files', 'loc', 'churn', 'fanIn', 'fanOut'];
/* a ref escapes the repo when its normalized form starts with ".." */
const escapesRepo = (ref) => {
  const out = [];
  for (const part of String(ref).split('#')[0].split('/')) {
    if (part === '' || part === '.') continue;
    if (part === '..') { if (out.length === 0 || out[out.length - 1] === '..') { return true; } out.pop(); }
    else out.push(part);
  }
  return false;
};
const DOC_KINDS = ['architecture-model', 'domain-model'];
const NODE_KINDS = ['module', 'package', 'service', 'component', 'store', 'entrypoint', 'external'];
const DOMAIN_NODE_KINDS = ['entity', 'action', 'state', 'policy'];
const EDGE_KINDS = ['depends', 'calls', 'publishes', 'consumes', 'reads', 'writes'];
const ARTIFACT_OWNERS = { 'architecture-model': 'andthen:map-codebase', 'domain-model': 'andthen:ubiquitous-language' };
const EDGE_EVIDENCE = ['imports', 'declared', 'git-coupling', 'inferred'];
const CTX_EVIDENCE = ['declared', 'inferred'];

let model = null;
try {
  model = JSON.parse(raw);
} catch (e) {
  err('model does not parse as JSON: ' + e.message);
}

if (model !== null) {
  if (typeof model !== 'object' || Array.isArray(model)) err('model root must be a JSON object');
  else {
    const isDomain = model.kind === 'domain-model';
    const nodeKinds = isDomain ? DOMAIN_NODE_KINDS : NODE_KINDS;
    if (model.schemaVersion !== '1') err('unsupported ' + (DOC_KINDS.includes(model.kind) ? model.kind : 'model') + ' schemaVersion ' + JSON.stringify(model.schemaVersion) + ' (expected "1")');
    if (!DOC_KINDS.includes(model.kind)) err('kind must be "architecture-model" or "domain-model", got ' + JSON.stringify(model.kind));

    const meta = model.meta;
    if (!meta || typeof meta !== 'object') err('meta object is required');
    else {
      if (!isStr(meta.project)) err('meta.project must be a non-empty string');
      if (!isStr(meta.generatedBy)) err('meta.generatedBy must be a non-empty string');
      if (typeof meta.date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(meta.date)) err('meta.date must be a YYYY-MM-DD string');
      if (meta.revision !== undefined && !isStr(meta.revision)) err('meta.revision must be a non-empty string when present');
      if (!isOptStr(meta.summary)) err('meta.summary must be a string when present');
    }

    const ctxIds = new Set();
    if (!Array.isArray(model.contexts) || model.contexts.length === 0) err('contexts must be a non-empty array');
    else model.contexts.forEach((c, i) => {
      const at = 'contexts[' + i + ']';
      if (!isStr(c.id)) err(at + '.id must be a non-empty string');
      else if (ctxIds.has(c.id)) err(at + ': duplicate context id "' + c.id + '"');
      else ctxIds.add(c.id);
      if (!isStr(c.name)) err(at + '.name must be a non-empty string');
      if (!CTX_KINDS.includes(c.kind)) err(at + '.kind must be one of ' + CTX_KINDS.join('|') + ', got ' + JSON.stringify(c.kind));
      if (!isStr(c.summary)) err(at + '.summary must be a non-empty string');
      if (!CTX_EVIDENCE.includes(c.evidence)) err(at + '.evidence must be one of ' + CTX_EVIDENCE.join('|') + ', got ' + JSON.stringify(c.evidence));
    });

    const nodeIds = new Set();
    if (!Array.isArray(model.nodes) || model.nodes.length === 0) err('nodes must be a non-empty array');
    else model.nodes.forEach((n, i) => {
      const at = 'nodes[' + i + ']' + (isStr(n.id) ? ' ("' + n.id + '")' : '');
      if (!isStr(n.id)) err(at + '.id must be a non-empty string');
      else if (nodeIds.has(n.id)) err(at + ': duplicate node id "' + n.id + '"');
      else nodeIds.add(n.id);
      if (!isStr(n.name)) err(at + '.name must be a non-empty string');
      if (!isStr(n.contextId)) err(at + '.contextId must be a non-empty string');
      else if (!ctxIds.has(n.contextId)) err(at + '.contextId "' + n.contextId + '" does not resolve to a context');
      if (!nodeKinds.includes(n.kind)) err(at + '.kind must be one of ' + nodeKinds.join('|') + ', got ' + JSON.stringify(n.kind));
      if (!isStr(n.ref)) err(at + '.ref is required (repo-relative path)');
      else {
        if (n.ref.startsWith('/') || n.ref.startsWith('~')) err(at + '.ref must be repo-relative, not absolute or home-anchored: "' + n.ref + '"');
        if (n.ref.includes('://')) err(at + '.ref must be a repo-relative path, not a URL: "' + n.ref + '"');
        if (escapesRepo(n.ref)) err(at + '.ref must not escape the repo via "..": "' + n.ref + '"');
      }
      if (!isOptStr(n.summary)) err(at + '.summary must be a string when present');
      if (n.metrics !== undefined) {
        if (!n.metrics || typeof n.metrics !== 'object' || Array.isArray(n.metrics)) err(at + '.metrics must be an object when present');
        else Object.entries(n.metrics).forEach(([k, v]) => {
          if (!METRIC_KEYS.includes(k)) err(at + '.metrics.' + k + ' is not a documented metric (allowed: ' + METRIC_KEYS.join(', ') + ')');
          else if (!isNonNegInt(v)) err(at + '.metrics.' + k + ' must be a non-negative integer, got ' + JSON.stringify(v));
        });
      }
      if (isDomain) {
        if (n.avoid !== undefined) {
          if (!Array.isArray(n.avoid) || n.avoid.length === 0) err(at + '.avoid must be a non-empty array when present (omit the key instead of [])');
          else n.avoid.forEach((a, j) => {
            if (typeof a !== 'string' || !a.trim()) err(at + '.avoid[' + j + '] must be a non-empty string, got ' + JSON.stringify(a));
          });
        }
        if (n.meanings !== undefined) {
          if (!Array.isArray(n.meanings)) err(at + '.meanings must be an array when present');
          else {
            if (n.meanings.length < 2) err(at + '.meanings must have at least 2 entries, found ' + n.meanings.length);
            const seenCtx = new Set();
            n.meanings.forEach((m, j) => {
              const mat = at + '.meanings[' + j + ']';
              if (!m || typeof m !== 'object' || Array.isArray(m)) { err(mat + ' must be an object'); return; }
              if (!isStr(m.label)) err(mat + '.label must be a non-empty string');
              if (!isStr(m.meaning)) err(mat + '.meaning must be a non-empty string');
              if (!isStr(m.contextId)) err(mat + '.contextId must be a non-empty string');
              else {
                if (!ctxIds.has(m.contextId)) err(mat + '.contextId "' + m.contextId + '" does not resolve to a context');
                if (seenCtx.has(m.contextId)) err(mat + '.contextId "' + m.contextId + '" duplicates another meaning (contextIds must be distinct)');
                seenCtx.add(m.contextId);
              }
            });
          }
        }
      }
    });

    if (!Array.isArray(model.edges)) err('edges must be present as an array (may be empty)');
    else if (isDomain && model.edges.length > 0) err('edges must be empty for a domain-model (found ' + model.edges.length + ')');
    (Array.isArray(model.edges) ? model.edges : []).forEach((e, i) => {
      const at = 'edges[' + i + ']';
      if (!isStr(e.from)) err(at + '.from must be a non-empty string');
      else if (!nodeIds.has(e.from)) err(at + '.from "' + e.from + '" does not resolve to a node');
      if (!isStr(e.to)) err(at + '.to must be a non-empty string');
      else if (!nodeIds.has(e.to)) err(at + '.to "' + e.to + '" does not resolve to a node');
      if (!EDGE_KINDS.includes(e.kind)) err(at + '.kind must be one of ' + EDGE_KINDS.join('|') + ', got ' + JSON.stringify(e.kind));
      if (!EDGE_EVIDENCE.includes(e.evidence)) err(at + '.evidence must be one of ' + EDGE_EVIDENCE.join('|') + ', got ' + JSON.stringify(e.evidence));
      if (!isOptStr(e.label)) err(at + '.label must be a string when present');
      if (e.weight !== undefined && !(Number.isInteger(e.weight) && e.weight > 0)) err(at + '.weight must be a positive integer when present');
    });

    if (model.tours !== undefined && !Array.isArray(model.tours)) err('tours must be an array when present');
    const tourIds = new Set();
    (Array.isArray(model.tours) ? model.tours : []).forEach((t, i) => {
      const at = 'tours[' + i + ']';
      if (!isStr(t.id)) err(at + '.id must be a non-empty string');
      else if (tourIds.has(t.id)) err(at + ': duplicate tour id "' + t.id + '"');
      else tourIds.add(t.id);
      if (!isStr(t.title)) err(at + '.title must be a non-empty string');
      if (!Array.isArray(t.steps) || t.steps.length === 0) err(at + '.steps must be a non-empty array');
      else t.steps.forEach((s, j) => {
        const sat = at + '.steps[' + j + ']';
        const hasNode = s.nodeId != null, hasCtx = s.contextId != null;
        if (hasNode === hasCtx) err(sat + ' must have exactly one non-null of nodeId or contextId');
        if (hasNode && !nodeIds.has(s.nodeId)) err(sat + '.nodeId "' + s.nodeId + '" does not resolve to a node');
        if (hasCtx && !ctxIds.has(s.contextId)) err(sat + '.contextId "' + s.contextId + '" does not resolve to a context');
        if (!isStr(s.note)) err(sat + '.note must be a non-empty string');
      });
    });
  }
}

if (errors.length) {
  console.error('render-atlas: model validation failed (' + errors.length + ' error(s)) for ' + srcArg);
  errors.forEach((m) => console.error('  - ' + m));
  process.exit(1);
}

/* ===================== inject + CSP hash + write ===================== */
/* exit 2 = renderer/template defect, never the artifact's fault (exit 1 is
   reserved for model validation so callers can route errors to the model owner) */
const failRenderer = (msg) => { console.error('render-atlas: renderer error (not an artifact problem): ' + msg); process.exit(2); };

let template;
try {
  template = fs.readFileSync(new URL('../templates/atlas.html', import.meta.url), 'utf8');
} catch (e) {
  failRenderer('cannot read templates/atlas.html next to this script: ' + e.message);
}

/* external-resource scan runs on the template, pre-injection: the injected JSON
   is inert data and may legitimately contain "url(http" or "@import" in summaries */
if (/src="http|href="http|url\(http|@import/.test(template)) failRenderer('external resources are forbidden in the template');

/* < > & and line separators escaped so serialized JSON can never form
   "</script" or "<!--" inside the inline script */
const jsonForHtml = (v) => JSON.stringify(v).replace(/[<>&\u2028\u2029]/g,
  (c) => ({ '<': '\\u003c', '>': '\\u003e', '&': '\\u0026', '\u2028': '\\u2028', '\u2029': '\\u2029' })[c]);

const SLOT = '/*__ATLAS_MODEL__*/null';
const slotCount = template.split(SLOT).length - 1;
if (slotCount !== 1) failRenderer('template must contain the ' + SLOT + ' slot exactly once (found ' + slotCount + ')');

const HASH_SLOT = '__ATLAS_CSP_HASH__';
if (template.split(HASH_SLOT).length - 1 !== 1) failRenderer('template must contain the ' + HASH_SLOT + ' CSP slot exactly once');

const boot = {
  artifactPath: srcArg,
  artifactOwner: ARTIFACT_OWNERS[model.kind],
  artifactSha1: crypto.createHash('sha1').update(srcArg).digest('hex'),
  model
};
let html = template.replace(SLOT, () => jsonForHtml(boot));

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (scripts.length !== 1) failRenderer('expected exactly one inline script in the template, found ' + scripts.length);
const hash = crypto.createHash('sha256').update(scripts[0]).digest('base64');
html = html.replace(HASH_SLOT, () => hash);

/* self-checks: Safe Output Boundary invariants on the emitted page.
   Markup-level checks are safe post-injection because jsonForHtml escapes
   every "<", so the payload can never form a tag or attribute. */
const emitted = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (emitted.length !== 1) failRenderer('emitted page must contain exactly one inline script');
if (!html.includes("script-src 'sha256-" + crypto.createHash('sha256').update(emitted[0]).digest('base64') + "'")) failRenderer('emitted script hash missing from CSP');
if (/<[^>]+\son[a-z]+=/i.test(html)) failRenderer('inline event handlers are forbidden in the output');
if (html.includes(String.fromCharCode(0))) failRenderer('NUL bytes leaked into the output');

fs.writeFileSync(outArg, html);
console.log(JSON.stringify({
  written: outArg,
  contexts: model.contexts.length,
  nodes: model.nodes.length,
  edges: Array.isArray(model.edges) ? model.edges.length : 0,
  tours: Array.isArray(model.tours) ? model.tours.length : 0,
  bytes: Buffer.byteLength(html)
}));
