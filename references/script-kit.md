# Reference: Script Kit

Paste these instead of writing them. Every block here ran in a full CREATE; composing the
same helpers fresh on every call is where most of a run's tokens and retries went.

## Find it by need

| Need | Block |
|---|---|
| Everything preflight asks, in two parallel calls | `PREFLIGHT_TARGET` + `PREFLIGHT_KIT` |
| Text, frames, kit instances, sections, mode-pinned cells | `PRELUDE` |
| Resolving a token through its alias chain; alpha-composited contrast | `PRELUDE` · `resolve`, `over`, `ratio` |
| The end-of-build validation: J1–J10, A9, A12, A14, L16–L19 | `SWEEP` |
| Recording the run in the kit config, one entry per component | `MERGE_RUN` |

---

## Budget rules

These cost more than anything else in a run. Each one is a habit, not a nicety.

1. **Two discovery calls, then write.** `PREFLIGHT_TARGET` and `PREFLIGHT_KIT`, issued in
   parallel in one message. Everything else a CREATE needs is in their output or in the
   config block. Do not read another sheet to copy its styles — the chrome constants are in
   `PRELUDE`.
2. **Four build calls for a CREATE**, one per chapter group: overview (00–01), structure
   (02–06), contract (07–09), usage + history (10–12). Then one `SWEEP`, one config merge.
   A call per section multiplies the prelude by thirteen.
3. **Return ids and counts, never dumps.** Cap any list at 10. A layer-tree dump is a
   one-time diagnostic, not a habit — the readout of a 9-variant set ran to thousands of
   tokens and one line per variant was all that was used.
4. **Screenshots: one after editing the component, one per chapter group at the end.**
   `scale: 1` or less. Never inline a screenshot in a script that also builds.
5. **Load references by symptom.** `figma-api-pitfalls.md` is read for its index; a section is
   read when its symptom appears. The rubric is read for AUDIT; a CREATE validates with
   `SWEEP` and reads a check's row only when it fails.
6. **Make every build call idempotent** — throw if its group already exists. A retry after a
   partial failure then costs one call, not a cleanup.

---

## `PREFLIGHT_TARGET`

Replace `TARGET`. One page switch.

```js
const TARGET = '852:851';
const node = await figma.getNodeByIdAsync(TARGET);
if (!node) return { error: `node ${TARGET} not found` };
let page = node; while (page.type !== 'PAGE') page = page.parent;
await figma.setCurrentPageAsync(page);
const set = node.type === 'COMPONENT' && node.parent?.type === 'COMPONENT_SET' ? node.parent : node;
const cols = await figma.variables.getLocalVariableCollectionsAsync();
const vars = await figma.variables.getLocalVariablesAsync();
const types = {}; for (const v of vars) types[v.resolvedType] = (types[v.resolvedType] || 0) + 1;
let defs = null, defsError = null;
try { defs = Object.entries(set.componentPropertyDefinitions).map(([k, v]) => `${k}:${v.type}${v.variantOptions ? '=' + v.variantOptions.join('|') : ''}`); }
catch (e) { defsError = e.message; }                         // "existing errors" = duplicate variant names
const names = set.type === 'COMPONENT_SET' ? set.children.map(c => c.name) : [];
const handoff = page.findOne(n => n.type === 'FRAME' && n.name === `DS · ${set.name} · Handoff`);
return {
  page: { id: page.id, name: page.name },
  target: { id: set.id, type: set.type, name: set.name, variants: names.length, layout: set.layoutMode, description: !!set.description },
  defs, defsError, duplicateVariants: names.filter((n, i) => names.indexOf(n) !== i),
  collections: cols.map(c => `${c.name} (${c.modes.map(m => m.name).join(', ')}) ${c.variableIds.length}`),
  varTypes: types, textStyles: (await figma.getLocalTextStylesAsync()).length,
  mode: handoff ? 'AUDIT or RE-AUDIT' : 'CREATE', handoff: handoff?.id ?? null,
};
```

## `PREFLIGHT_KIT`

Issue in the same message as `PREFLIGHT_TARGET`. Reads the config block and the kit's main
component ids — the ids every build call needs — so nothing looks them up again.

```js
const COMPONENT = 'Badge';
const kit = figma.root.children.find(p => p.name === '_docs-kit');
if (!kit) return { kit: 'missing' };
await figma.setCurrentPageAsync(kit);
const cfg = kit.findOne(n => n.type === 'TEXT' && n.name === 'config');
// everything above `runs:`, plus this component's entry only — the block grows with every component documented
const text = cfg?.characters ?? '';
const head = text.split(/^runs:\s*$/m)[0].replace(/^lastRun:[\s\S]*$/m, '').trim();
const run = (text.match(new RegExp(`^  ${COMPONENT}:\\s*\\n((?:    .*\\n?)*)`, 'm')) || [])[1] ?? null;
const legacy = /^lastRun:/m.test(text);
const ids = {};
for (const n of kit.findAllWithCriteria({ types: ['COMPONENT'] })) {
  const owner = n.parent.type === 'COMPONENT_SET' ? n.parent.name : n.name;
  if (owner.startsWith('_docs/')) (ids[owner.slice(6)] ??= {})[n.parent.type === 'COMPONENT_SET' ? n.name : '-'] = n.id;
}
return { config: cfg ? head : null, run, legacyLastRun: legacy, ids };
```

---

## `PRELUDE`

Paste at the top of every build call. The chrome constants are the generic language from
[visual-design.md](visual-design.md); the kit ids come from `PREFLIGHT_KIT`.

```js
await Promise.all([['Inter','Regular'],['Inter','Bold'],['Inter','Semi Bold'],['DM Mono','Regular']].map(([family, style]) => figma.loadFontAsync({ family, style })));
const C = { ink: [0.11,0.13,0.16], muted: [0.42,0.45,0.5], muteDk: [0.65,0.68,0.72], teal: [0.06,0.46,0.43], tint: [0.969,0.973,0.98], code: [0.976,0.98,0.984], rule: [0.89,0.9,0.92] };
const rgb = a => ({ r: a[0], g: a[1], b: a[2] });
const T = { title: ['Inter','Bold',44,52,-2,'ink'], desc: ['Inter','Regular',18,28,0,'muted'], body: ['Inter','Regular',14,20,0,'ink'],
  caption: ['Inter','Regular',12,18,0,'muted'], note: ['Inter','Regular',12,18,0,'teal'], label: ['Inter','Semi Bold',11,16,0,'muted'],
  tag: ['DM Mono','Regular',12,18,0,'muted'], mono: ['DM Mono','Regular',12,18,0,'ink'], spec: ['DM Mono','Regular',11,17,0,'ink'] };
// width: number → FIXED and wrapping · 'FILL' → fills a FIXED-width ancestor · omitted → hugs
function text(parent, name, chars, style, width) {
  const [f, s, size, lh, ls, c] = T[style]; const t = figma.createText(); t.name = name;      // always named (§19)
  t.fontName = { family: f, style: s }; t.fontSize = size; t.lineHeight = { unit: 'PIXELS', value: lh };
  if (ls) t.letterSpacing = { unit: 'PERCENT', value: ls };
  t.fills = [{ type: 'SOLID', color: rgb(C[c]) }]; t.characters = chars; parent.appendChild(t);
  if (width === 'FILL') { t.textAutoResize = 'HEIGHT'; t.layoutSizingHorizontal = 'FILL'; }
  else if (typeof width === 'number') { t.textAutoResize = 'HEIGHT'; t.resize(width, t.height); if (parent.layoutMode && parent.layoutMode !== 'NONE') t.layoutSizingHorizontal = 'FIXED'; }
  else t.textAutoResize = 'WIDTH_AND_HEIGHT';
  return t;
}
function frame(parent, name, dir, o = {}) {
  const f = figma.createAutoLayout(dir); f.name = name; f.fills = []; if (parent) parent.appendChild(f);
  if (o.gap != null) f.itemSpacing = o.gap; if (o.pad) [f.paddingTop, f.paddingRight, f.paddingBottom, f.paddingLeft] = o.pad;
  if (o.fill) f.layoutSizingHorizontal = 'FILL'; if (o.bg) f.fills = [{ type: 'SOLID', color: rgb(C[o.bg] ?? o.bg) }]; if (o.r) f.cornerRadius = o.r;
  return f;
}
function cell(parent, name, w, h = 48) {                     // fixed table cell — J8
  const c = frame(parent, name, 'HORIZONTAL'); c.resize(w, h);
  c.primaryAxisSizingMode = 'FIXED'; c.counterAxisSizingMode = 'FIXED'; c.counterAxisAlignItems = 'CENTER'; return c;   // §3: modes after resize
}
async function inst(parent, id, props = {}) {                // text properties by name prefix; pick the variant by main id
  const m = await figma.getNodeByIdAsync(id); const i = m.createInstance(); parent.appendChild(i);
  const set = {}; for (const [k, v] of Object.entries(props)) {
    const key = Object.keys(i.componentProperties).find(d => d.split('#')[0] === k);
    if (!key) throw new Error(`no property ${k} on ${m.name}`); set[key] = v; }
  if (Object.keys(set).length) i.setProperties(set); return i;
}
async function section(group, num, title) {
  const s = frame(group, `${num} · ${title}`, 'VERTICAL', { gap: 20, fill: true });
  (await inst(s, KIT.section, { title, number: num })).layoutSizingHorizontal = 'FILL'; return s;
}
async function chapter(root, key, range, label) {
  if (root.findOne(n => n.name === `group · ${key}`)) throw new Error(`group · ${key} already exists`);   // idempotent
  const g = frame(root, `group · ${key}`, 'VERTICAL', { gap: 48, fill: true });
  (await inst(g, KIT.group, { range, label })).layoutSizingHorizontal = 'FILL'; return g;
}

// ---- tokens: one resolver and one compositing helper for the whole run (E0) ----
const cols = await figma.variables.getLocalVariableCollectionsAsync();
const sem = cols.find(c => c.name === 'Semantic');
const LIGHT = sem.modes[0].modeId, DARK = sem.modes[1].modeId;
const vars = await figma.variables.getLocalVariablesAsync();
const V = new Map(vars.map(v => [v.name, v])), byId = new Map(vars.map(v => [v.id, v]));
function resolve(v, semMode) {
  for (let d = 0; d < 12; d++) { const col = cols.find(c => c.id === v.variableCollectionId);
    const val = v.valuesByMode[col.id === sem.id ? semMode : col.defaultModeId];
    if (val?.type === 'VARIABLE_ALIAS') { v = byId.get(val.id); continue; } return val; }
}
const over = (fg, a, bg) => ({ r: fg.r * a + bg.r * (1 - a), g: fg.g * a + bg.g * (1 - a), b: fg.b * a + bg.b * (1 - a) });
const lum = c => { const f = x => x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const themed = (node, mode, token = 'color/background/default') => {   // a cell or panel that shows the real theme
  node.fills = [figma.variables.setBoundVariableForPaint({ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }, 'color', V.get(token))];
  node.setExplicitVariableModeForCollection(sem, mode);
};
```

Define `KIT` from `PREFLIGHT_KIT` before the prelude runs — `const KIT = { section: '…', group: '…', … }`.

---

## `SWEEP`

Read-only. Run once after the last build call; it replaces reading the rubric to validate a
CREATE. Every count must be zero, `sections` must be 13 and `nameMatches` must equal it.

```js
const ROOT_ID = '1133:82';
const root = await figma.getNodeByIdAsync(ROOT_ID);
let pg = root; while (pg.type !== 'PAGE') pg = pg.parent; await figma.setCurrentPageAsync(pg);
const sections = root.findAll(n => n.type === 'FRAME' && /^\d\d · /.test(n.name) && n.parent && /^group · /.test(n.parent.name));
const lineH = t => t.lineHeight?.unit === 'PIXELS' ? t.lineHeight.value : (typeof t.fontSize === 'number' ? t.fontSize * 1.4 : 20);
const text = [];
for (const t of root.findAll(n => n.type === 'TEXT' && n.visible)) {
  const p = [];
  if (t.textAutoResize === 'NONE' || t.textAutoResize === 'TRUNCATE') p.push('J1');
  if (t.layoutSizingHorizontal === 'FILL' && t.textAutoResize === 'WIDTH_AND_HEIGHT') p.push('J2');
  if (t.textAutoResize === 'HEIGHT' && t.height > lineH(t) * 1.6 && t.characters.length < 24) p.push('J5');
  if (t.characters.length > 1 && t.width < 8) p.push('J6');
  if (p.length) text.push(`${t.name}: ${p.join(',')}`);
}
const J4 = root.findAll(n => n.type === 'FRAME' && n.layoutMode && n.layoutMode !== 'NONE').filter(c =>
  (c.layoutMode === 'HORIZONTAL' ? c.primaryAxisSizingMode : c.counterAxisSizingMode) === 'AUTO' && c.children.some(k => k.layoutSizingHorizontal === 'FILL')).map(c => c.name);
const DECOR = /^(focus-ring|halo|shadow)\b/i, OPAQUE = new Set(['COMPONENT_SET', 'COMPONENT', 'INSTANCE']);
const J9 = [];
for (const s of sections) (function walk(p) { if (!('children' in p)) return;
  const auto = p.layoutMode && p.layoutMode !== 'NONE';
  const left = auto ? p.paddingLeft || 0 : 0, right = p.width - (auto ? p.paddingRight || 0 : 0);
  for (const c of p.children) { if (!c.visible || DECOR.test(c.name)) continue;
    if (c.x < left - 0.5 || c.x + c.width > right + 0.5) J9.push(`${s.name} › ${c.name}`);
    if (!OPAQUE.has(c.type)) walk(c); } })(s);
const J10 = root.findAll(n => n.layoutWrap === 'WRAP' && n.layoutSizingHorizontal === 'HUG').map(n => n.name);
let A9 = 0; const A12 = [];
for (const i of root.findAllWithCriteria({ types: ['INSTANCE'] })) {
  const m = await i.getMainComponentAsync(); if (!m) { A9++; continue; }
  if (m.parent?.name === '_docs/Token Row') {
    const p = Object.fromEntries(Object.entries(i.componentProperties).map(([k, v]) => [k.split('#')[0], v.value]));
    for (const nm of ['token', 'property']) if (i.findOne(n => n.name === nm)?.characters !== p[nm]) A12.push(`${p.token} ${nm}`);
  }
}
// A14: the bare name count, compared with `sections`. Counting only — using it to find
// sections would be WRONG (§19); a larger number means a TEXT node collides with a section name.
return { sections: sections.length, nameMatches: root.findAll(n => /^\d\d · /.test(n.name)).length,
  text: text.slice(0, 10), J4, J9: J9.slice(0, 10), J9count: J9.length, J10, A9, A12: A12.slice(0, 10) };
```

Token-row swatch checks (`L16`–`L19`) need the resolver from `PRELUDE`; run them in the same
call by pasting the resolver above this block.

---

## `MERGE_RUN`

The last call of every run. Updates **this component's entry under `runs`** and nothing else;
a legacy single `lastRun` is migrated into `runs` on the way. Fill `RUN` with the run's YAML,
unindented. `SWEEP` can share the last build call; this one cannot — it is on the kit page.

```js
const COMPONENT = 'Badge';
const RUN = `node: "330:44"
at: 2026-10-12
counts: { blockers: 1, warnings: 2, info: 1 }
findings:
  - { id: B3, node: "330:44" }`;
const kit = figma.root.children.find(p => p.name === '_docs-kit'); await figma.setCurrentPageAsync(kit);
const cfg = kit.findOne(n => n.type === 'TEXT' && n.name === 'config');
if (!cfg) throw new Error('config block not found — never write one blind');
for (const s of cfg.getStyledTextSegments(['fontName'])) await figma.loadFontAsync(s.fontName);
const KEY = /^([A-Za-z][\w-]*):/;
const blocks = []; for (const l of cfg.characters.split('\n')) { if (KEY.test(l) || !blocks.length) blocks.push([l]); else blocks[blocks.length - 1].push(l); }
const keyOf = b => (b[0].match(KEY) || [])[1];
const runs = new Map();
const ri = blocks.findIndex(b => keyOf(b) === 'runs');
if (ri >= 0) { let cur = null; for (const l of blocks[ri].slice(1)) { const m = l.match(/^  ([^\s:][^:]*):\s*$/);
  if (m) runs.set(cur = m[1], []); else if (cur && l.startsWith('    ')) runs.get(cur).push(l.slice(4)); } }
const li = blocks.findIndex(b => keyOf(b) === 'lastRun');                   // legacy single slot
if (li >= 0) { const body = blocks[li].slice(1).filter(l => l.startsWith('  ')).map(l => l.slice(2));
  const c = (body.find(l => l.startsWith('component:')) || '').split(':')[1]?.trim();
  if (c && !runs.has(c)) runs.set(c, body.filter(l => !l.startsWith('component:'))); }
runs.set(COMPONENT, RUN.split('\n'));
const kept = blocks.filter((b, i) => i !== li && i !== ri);
const keysBefore = kept.map(keyOf).filter(Boolean);
cfg.characters = [...kept, ['runs:', ...[...runs].flatMap(([c, body]) => [`  ${c}:`, ...body.map(l => '    ' + l)])]].map(b => b.join('\n')).join('\n');
const keysAfter = cfg.characters.split('\n').map(l => (l.match(KEY) || [])[1]).filter(Boolean);
if (keysBefore.some(k => !keysAfter.includes(k))) throw new Error('merge dropped a top-level key');
return { mutatedNodeIds: [cfg.id], runs: [...runs.keys()], migratedLegacy: li >= 0 };
```
