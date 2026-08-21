# Reference: Visual Design

A handoff frame can be completely correct and still fail, because nobody reads 10,000px of
undifferentiated column. This is the layer that makes a correct document a usable one.

The failure it fixes: 13 sections, uniform 56px gaps, one flat surface. Everything is
equally related to everything else, so nothing is grouped, and there are no landmarks to
scan by.

---

## 1. Proximity — spacing encodes hierarchy

Uniform spacing is the default and it is always wrong. If `01 · Component` sits as far from
`02 · Anatomy` as `07 · Tokens` sits from `08 · Spec`, the layout is asserting they are
equally related. They are not.

| Level | Gap |
|---|---|
| Between chapters | 96 |
| Between sections in a chapter | 48 |
| Section header → its content | 20 |
| Rows inside a block | 12 |

The **ratio** matters more than the numbers — roughly 2× per level. Compress them all and
the hierarchy disappears; that is the same bug at a smaller scale.

Root padding: 80 sides, 72 top, 96 bottom.

---

## 1b. Chrome is generic — ask, don't assume

Documentation chrome does not use the file's design system by default. Same argument as
type (docs-kit.md): token names are per-file, so chrome bound to `color/surface/popover`
works in one file and degrades in the next. It also means a product retheme silently
restyles the documentation.

**Ask at preflight**, and default to generic:

```
Chrome styling for this handoff frame?
  1. Generic  (default) — self-contained palette, renders identically in any file
  2. File design system — chrome binds this file's semantic tokens; matches the
     product surface, but breaks when ported and moves when the product rethemes
```

### The default palette

Verified against every chrome surface; contrast noted for the worst case.

| Role | Value | Notes |
|---|---|---|
| `page` | `#F5F6F8` | The frame background |
| `card` | `#FFFFFF` | Content blocks |
| `code` | `#F9FAFB` | Spec block |
| `border` | `#E3E6EA` | Dividers, card edges |
| `text` | `#101828` | 16.4 : 1 worst case |
| `muted` | `#5C6672` | 5.4 : 1 worst case |

Two text tiers only. A third tier lands under 4.5 : 1 on a white card unless it is so close
to `muted` that it carries no distinction — measured, not guessed.

| Tone | bg | fg | border | fg-on-bg |
|---|---|---|---|---|
| neutral | `#F2F4F7` | `#475467` | `#D0D5DD` | 6.98 |
| info | `#EFF8FF` | `#175CD3` | `#B2DDFF` | 5.57 |
| success | `#ECFDF3` | `#067647` | `#ABEFC6` | 5.40 |
| warning | `#FFFAEB` | `#B54708` | `#FEDF89` | 5.20 |
| danger | `#FEF3F2` | `#B42318` | `#FECDCA` | 6.05 |

### What stays on the file's tokens — always, in both modes

| Generic chrome | File tokens |
|---|---|
| Page, cards, rules, section headers | The documented component and every instance of it |
| Tables, badges, chips, prose | **Its part sets** — they are the component too |
| The spec block | **Mode panels** — they exist to show the real theme |
| | **Token swatches** — they *are* the tokens |

---

## 1c. The frame is a sheet on a canvas — not a panel

Figma's canvas is mid-grey. A page surface in the same family (`#F5F6F8` and similar)
**disappears into it** — the document has no edge, and the whole thing reads as canvas.

The document is a **sheet**:

```
root   fill #FFFFFF · radius 28 · 1px #E3E6EA
       shadow  y 28 · blur 72 · spread −12 · rgba(16,24,40,0.10)
```

Inner blocks then tint *downward* from the sheet, not upward from a grey page:

```
block  fill #F7F8FA · radius 16 · NO border
```

This inverts the obvious move — page recedes, cards lift — and it is the right way round
here, because the competing surface is Figma's canvas, not the page. A white sheet with a
soft shadow reads as a document at any zoom.

**Borderless tinted blocks are also the fix for "blocky".** A border plus a tint plus a
radius is three separations doing one job; the result is a stack of slabs. The tint alone
is enough.

---

## 1d. Type scale — documents are read at zoom-to-fit

A scale tuned at 100% is too small for a 1280-wide document that people mostly view zoomed
out. Everything moves up a step:

| Role | Size / line | Weight |
|---|---|---|
| `display` — component name | 44 / 52, −2% | Bold |
| `title` — section | 28 / 36, −1% | Semi Bold |
| `subhead` | 20 / 28 | Semi Bold |
| `bodyLg` — component description | 18 / 28 | Regular |
| `body` | 14 / 20 | Regular |
| `label` | 13 / 20 | Medium |
| `chapter` | 13 / 18, +10% | Semi Bold, uppercase |
| `mono` | 13–14 / 20 | Regular |

The section title at 28 against body at 14 is a 2× step. At 20 it was 1.4× and read as
emphasis rather than hierarchy.

---

## 1e. Not every block is a card

Full-width card, full-width card, full-width card is the blocky failure. Three fixes:

1. **Pair thin sections side by side.** Two "not applicable" notes are one row, not two
   full-width slabs.
2. **Leave prose uncarded.** A measured paragraph under a section header needs no
   container — the header and the whitespace already group it.
3. **Card only what is scanned**: matrices, tables, code blocks, rendered examples.

---

## 2. Common region — card the data, not the labels

Content blocks sit inside cards; the page recedes behind them.

```
sheet (root)  #FFFFFF · radius 28 · 1px #E3E6EA · soft shadow
block         #F7F8FA · radius 16 · NO border · padding 32
```

**Section headers stay on the page**, outside the card. That is what makes them read as
labels *for* the block below rather than part of it.

Card: tables, matrices, code blocks, rendered examples, mode panels.
Don't card: section headers, captions, single lines of prose.

### Don't card small things

A keycap is a chip. A status badge is a chip. Applying 32px padding and a 16px radius to
everything with a fill turns them into slabs. Gate the treatment on size — roughly, only
blocks wider than ~400px.

---

## 3. Figure / ground — the check that fails silently

If the page and a card resolve to the **same surface token**, the card vanishes. There is
no error; the structure is perfect and the document just looks flat.

Changing the page surface means re-checking every inner surface. When this frame's root
moved to `surface/sunken`, four inner blocks that were also `surface/sunken` disappeared in
the same commit.

**After any surface change, sweep for children whose fill token equals the page's.**

---

## 4. Similarity — a group header is not a bigger section header

The tempting move is to make the chapter title larger. It doesn't work: at 24px next to a
20px section title it reads as *the same level, slightly louder*, and the eye can't tell a
chapter boundary from a section boundary.

Give it a **different treatment** instead, so it reads as a different kind of thing:

| | Chapter | Section |
|---|---|---|
| Rule | 2px, `foreground/default` | 1px, `border/subtle` |
| Label | 12 Semi Bold, UPPERCASE, 8% tracking | 20 Semi Bold, sentence case |
| Position | above the group | above the section |

The chapter is a divider carrying a label. The section is a title. Different job, different
shape.

---

## 4b. Anatomy pins belong in a gutter, not on the artwork

**Choose the gutter axis from how the parts are distributed, not by default.** Measure the
spread of the part centres before placing anything:

```js
const xSpread = Math.max(...cx) - Math.min(...cx);
const ySpread = Math.max(...cy) - Math.min(...cy);
const axis = xSpread > ySpread ? 'bottom gutter, vertical leaders'
                               : 'left gutter, horizontal leaders';
```

A left gutter assumes the parts are stacked vertically. A horizontal control breaks that
assumption completely: an inline control's leading icon, label and trailing icon spread
**horizontally with effectively no vertical spread** — they share one vertical centre. Placing their pins in a
left gutter stacks all three at the same `y`, and the collision rule then pushes two of them
off the parts they point at, which is the exact failure the gutter was introduced to avoid.

A part whose own axis differs from the rest — the container, for instance — takes the axis
that suits it. Mixing one left pin with three bottom pins reads correctly; forcing all four
onto one axis does not.

Pins dropped onto the component cover the thing they are annotating, collide where parts
nest, and read as damage rather than annotation.

Put them in a **left gutter** with leader lines:

```
gutter 40 ─ pin 24 ─ leader hairline ─── artwork at x 132 ─── legend at artwork right + 104
```

- One pin per legend entry, at the **vertical centre** of its part
- A 1px hairline from the pin to the part's left edge
- **Sort anchors by y before placing**, then push any pin less than `PIN + 6` from the
  previous one down. Sorted order is what guarantees the leader lines never cross
- Anchor a container at its **bottom** edge so its pin doesn't collide with the pin of the
  first child inside it

The artwork stays uncovered, the numbers stay tied to the legend, and the section finally
reads as a diagram.

---

## 5. Measure — line length is a correctness issue

Prose at 1152px and 14px is about **160 characters per line**. Comfortable measure is
45–75. Long lines make the reader lose their place on every return sweep, and no amount of
correct content survives that.

| Content | Width |
|---|---|
| Prose — descriptions, captions, notes, changelog | **760** (`FIXED`, `textAutoResize: HEIGHT`) |
| Tables, matrices, code blocks | Full width — these are *scanned*, not read |
| Section header description | 760, set on the kit main so every section inherits it |

Recipe #2 from [text-layout.md](text-layout.md): resize first, then `FIXED`.

---

## 6. Grouping — contiguous, always

```
Overview    00 – 01   Header, Component
Structure   02 – 06   Anatomy, Modes, Variants, Sizes, States
Contract    07 – 09   Tokens, Spec, Accessibility
Usage       10 – 11   Content, Do / Don't
History     12        Changelog
```

**Group contiguously by section number.** A thematically tidier grouping that reorders
sections (Modes with Tokens, say) breaks the numbering, the reading order, and every
reference to "section 03". Not worth it.

Groups are **visual chunking only**. Section numbers remain the contract; group names are
not addressable and can be renamed freely.

### Consequence for discovery

Sections are no longer direct children of the root. Anything that walked `root.children`
must now search:

```js
const sections = root.findAll(n => n.type === 'FRAME'
                                 && /^\d\d · /.test(n.name)
                                 && n.parent && /^group · /.test(n.parent.name));
```

---

## 7. Order of operations

Visual work comes **last**, after the content is correct and audited. Regrouping a frame
reparents every section, so doing it before the content settles means doing it twice.

Then, because reparenting and re-surfacing touch every node:

1. Re-run the [text-layout](text-layout.md) sweep — new widths mean new wrap risks
2. Sweep for unbound chrome paints — see figma-api-pitfalls.md §14
3. Re-check instance integrity — moving sets and instances is when orphans appear
4. **Confirm content bindings survived.** Every paint inside the documented component and
   its part sets must still be variable-bound. This is the check that catches a styling
   pass that reached into content — see figma-api-pitfalls.md §15

All four must return zero. A visually improved frame that broke its own bindings is a
regression, not an improvement.
