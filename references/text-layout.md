# Reference: Text Layout

The most common way agent-built Figma output is quietly wrong. Every script reports
success, the structure is correct, and the text renders as `1` over `0` — or as `1 . 2 . 0`
down five lines.

## Find it by symptom

| Symptom | Where |
|---|---|
| A short string wraps one character per line | §The rule · starved `FILL` |
| `"10"` renders as `1` over `0` | §The rule |
| A text node is 1px wide | §The rule · no fixed-width ancestor |
| Every row of a generated table is ~10px tall | §Creation order |
| A column's labels no longer line up across rows | Recipe 2 · columns must be `FIXED` |
| Text is clipped at the bottom | Tuning · check the style's line-height first |
| A single glyph reports a tiny width | Tuning · legitimate, do not flag |
| Content overflows a fixed-height cell | The sweep · overflow check |

**Run the sweep at the end of every build.** It is cheap and it catches what screenshots
of one section will not.

---

## The rule everything follows from

**`FILL` is a promise deferred upward.** A text node set to `layoutSizingHorizontal = 'FILL'`
does not have a width — it inherits whatever width its ancestor chain actually pins.

If every ancestor hugs, `FILL` resolves to the *content* width. Then a short string wraps
character by character, because the box collapsed to nothing and the text is trying to fit
inside it.

Observed in this file: a `value` layer at **1px wide**, rendering `v2` as `v` over `2`, and
`1.2.0` down five lines. Its row was `FIXED` at an arbitrary 152px inside a parent set to
hug, so the FILL text got `152 − label 140 − gap = 1px`.

**A `FILL` text node needs a `FIXED`-width ancestor. Verify it, don't assume it.**

---

## The four valid recipes

Any other combination is a bug.

### 1. Wrapping body text

```js
parent.layoutSizingHorizontal = 'FILL';   // or FIXED — must resolve to a real width
text.layoutSizingHorizontal = 'FILL';
text.textAutoResize = 'HEIGHT';           // width from parent, height from content
```

### 2. Fixed column inside a row

```js
text.textAutoResize = 'HEIGHT';
text.resize(140, text.height);            // resize BEFORE sizing — resize resets modes
text.layoutSizingHorizontal = 'FIXED';
```

Column layers must be `FIXED`. A hugging label collapses to its content and the column
alignment dies across every row at once.

Only the **last** column in a row uses `FILL`.

### 3. Hugging label, chip, badge

```js
text.textAutoResize = 'WIDTH_AND_HEIGHT';  // parent hugs around it
```

### 4. Centered in a fixed-size cell

```js
cell.primaryAxisSizingMode = 'FIXED';
cell.counterAxisSizingMode = 'FIXED';
cell.primaryAxisAlignItems = 'CENTER';
cell.counterAxisAlignItems = 'CENTER';
text.layoutSizingHorizontal = 'FILL';
text.textAutoResize = 'HEIGHT';
text.textAlignHorizontal = 'CENTER';
```

A fixed-height cell is **not** a bug — it is how a fixed 32×32 icon slot is supposed to work.
Only flag it when the text actually overflows.

### Never

| Anti-pattern | Why |
|---|---|
| `textAutoResize = 'NONE'` / `'TRUNCATE'` | A fixed box that clips silently |
| `FILL` + `WIDTH_AND_HEIGHT` | Hug fights fill; hug wins and the box collapses |
| `FILL` text under an all-hugging ancestor chain | No real width to inherit |
| A container that hugs horizontally holding a `FILL` child | The trap above, one level up |

---

## The container trap

This is the shape to search for. It is always wrong:

```js
container.layoutMode === 'VERTICAL' && container.counterAxisSizingMode === 'AUTO'
  && container.children.some(c => c.layoutSizingHorizontal === 'FILL')
```

A hugging container asks its children how wide to be; a `FILL` child asks the container.
Neither has an answer, so both collapse.

Fix by pinning the container:

```js
container.counterAxisSizingMode = 'FIXED';
container.resize(width, container.height);
container.primaryAxisSizingMode = 'AUTO';
container.layoutSizingHorizontal = 'FILL';   // now defers to a parent that IS fixed
for (const row of container.children) row.layoutSizingHorizontal = 'FILL';
```

---

## The sweep

Run over the whole handoff frame **and** the kit page after every build.

```js
function lineH(t){
  if (t.lineHeight?.unit === 'PIXELS') return t.lineHeight.value;
  if (t.lineHeight?.unit === 'PERCENT' && typeof t.fontSize === 'number')
    return t.fontSize * t.lineHeight.value / 100;
  return typeof t.fontSize === 'number' ? t.fontSize * 1.4 : 20;
}
function clipsAbove(t, root){
  let n = t.parent;
  while (n && n.id !== root.id) { if (n.clipsContent) return n.name; n = n.parent; }
  return null;
}

const issues = [];
for (const t of root.findAll(n => n.type === 'TEXT')) {
  const lh = lineH(t), p = t.parent, probs = [];

  if (t.textAutoResize === 'NONE' || t.textAutoResize === 'TRUNCATE') probs.push('tar=' + t.textAutoResize);
  if (t.layoutSizingHorizontal === 'FILL' && t.textAutoResize === 'WIDTH_AND_HEIGHT') probs.push('FILL + WIDTH_AND_HEIGHT');

  // a single glyph is legitimately narrow — only multi-char text signals a starved box
  if (t.characters.length > 1 && t.width < 8) probs.push('collapsed width ' + Math.round(t.width));

  // the signature of a starved FILL: a short string wrapping
  if (t.textAutoResize === 'HEIGHT' && t.height > lh * 1.6 && t.characters.length < 24)
    probs.push(`short string over ${Math.round(t.height / lh)} lines at w ${Math.round(t.width)}`);

  // clipping only counts when an ancestor actually clips
  const clipper = clipsAbove(t, root);
  if (clipper && p?.layoutMode && p.layoutMode !== 'NONE') {
    const fixedH = p.layoutMode === 'HORIZONTAL'
      ? p.counterAxisSizingMode === 'FIXED' : p.primaryAxisSizingMode === 'FIXED';
    const inner = p.height - (p.paddingTop || 0) - (p.paddingBottom || 0);
    if (fixedH && t.height > inner + 0.5) probs.push(`overflows clipping parent "${clipper}"`);
  }
  if (probs.length) issues.push({ name: t.name, chars: t.characters.slice(0, 28), w: Math.round(t.width), probs });
}
```

Plus the container check:

```js
const risky = root.findAll(n => (n.type === 'FRAME' || n.type === 'COMPONENT') && n.layoutMode && n.layoutMode !== 'NONE')
  .filter(c => {
    const hugsH = c.layoutMode === 'HORIZONTAL' ? c.primaryAxisSizingMode === 'AUTO' : c.counterAxisSizingMode === 'AUTO';
    return hugsH && c.children.some(k => k.layoutSizingHorizontal === 'FILL');
  });
```

**Both must return zero.**

---

## Tuning — three false positives to avoid

An over-eager sweep is worse than none; it trains you to ignore the output. The first run
of this sweep flagged **190 of 423** text nodes, of which **7** were real.

| False positive | Why it isn't a bug | Correct test |
|---|---|---|
| Fixed-height parent | A 32×32 cell is deliberate | Only flag if text height > parent inner height |
| Single glyph at 6px wide | `1` in a 24px pin is correct | Require `characters.length > 1` |
| Height < font size | A type system may set `lineHeight ≤ fontSize` on purpose — `Label/Badge` here is 11/11 | Compare against the **style's** `lineHeight`, and only flag when an ancestor clips |

Read the type style before calling a tight line-height a defect.

---

## Creation order — the same rule, one step earlier

The `resize()` trap does not only bite when *fixing* a node. It bites hardest when
**creating** one, because the natural way to write it is wrong:

```js
// WRONG — reads correctly, pins the frame at 10px tall
c.primaryAxisSizingMode = 'FIXED';
c.counterAxisSizingMode = 'AUTO';
c.resize(1000, 10);            // resets counterAxis to FIXED at height 10

// CORRECT — resize, then declare how it should size
c.primaryAxisSizingMode = 'FIXED';
c.resize(1000, c.height);
c.counterAxisSizingMode = 'AUTO';   // hug height, AFTER
```

Symptom: every row of a generated table collapses to a sliver with the text overlapping.
The script reports success and returns valid node IDs.

Write it as a helper and use it everywhere a component is built:

```js
function sizeFrame(node, width) {
  if (node.layoutMode === 'HORIZONTAL') {
    node.primaryAxisSizingMode = 'FIXED';
    node.resize(width, node.height);
    node.counterAxisSizingMode = 'AUTO';
  } else {
    node.counterAxisSizingMode = 'FIXED';
    node.resize(width, node.height);
    node.primaryAxisSizingMode = 'AUTO';
  }
}
```

---

## Ordering, again

Every fix in this file interacts with the two rules in figma-api-pitfalls.md:

1. **`resize()` resets sizing modes** (§3) — resize first, then set `FILL` / `AUTO`.
2. **`primaryAxisSizingMode` is width for `HORIZONTAL`, height for `VERTICAL`** (§4) —
   "hug height" is the opposite call depending on direction.

Getting either wrong produces exactly the symptoms above, which is why a text problem is
so often really a container problem one or two levels up.

---

## The heuristic: characters per line, not raw width

The first version of this sweep flagged **190 of 423** nodes, of which 7 were real. A later
version keyed on `textAutoResize === 'HEIGHT' && width < 200` and flagged **89** — every one
of them a kit `Meta Row` label sitting in a correctly-designed fixed 160px label column.

**Raw width is not the signal.** A narrow text node is only a bug if it is narrow *relative
to what it has to say*. The real failure — FILL text starved inside a hug parent — shows up
as text wrapping one or two characters per line.

```js
const lh    = (t.lineHeight && t.lineHeight.value) || t.fontSize * 1.2;
const lines = Math.max(1, Math.round(t.height / lh));

if (t.height < 6)                                    flag('collapsed');
else if (t.width < 40 && t.characters.length > 12)   flag('starved');
else if (t.characters.length > 30
         && t.characters.length / lines < 6)         flag('wrapping per character');

if (t.parent && t.parent.clipsContent && t.width > t.parent.width + 1) flag('clipped');
```

With that heuristic the same frame returned **830 text nodes, 0 issues** — and the issues it
had found earlier were all still caught in the runs where they were real.

Short labels are not bugs. A section number reading `10`, a badge reading `Do`, a column
header reading `TYPE` — all legitimately under 40px. A check that flags them is worse than
no check, because the reader learns to skim past its output.

