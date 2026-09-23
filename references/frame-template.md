# Reference: Handoff Frame Template

The handoff frame is a **frame, not a page**. Several components can share a page — a
Badge does not deserve its own. Pages group by domain (`Components · Forms`); frames hold
the handoff.

---

## Root frame

```
Name        DS · {Component} · Handoff      ← the discovery contract. No plugin data exists.
Type        FRAME, auto-layout VERTICAL
Width       1280 (FIXED)
Height      HUG
Padding     64
Item gap    56
Fill        #FFFFFF · radius 28 · 1px #E3E6EA · soft shadow — the sheet
```

Position to the right of the component it documents, with a clear gutter. Never at (0,0).

**`content = width − 2 × padding` is the constant every section is laid out against.**
Settle it before building the first section. The visual pass changes root padding, and if
the content column moves afterwards, every fixed-width table beneath it overflows its
parent. Either hold `content` fixed and grow the sheet, or build tables that FILL.

**When the documented component is wider than the content column**, widen the sheet rather
than clipping or scaling it:

```
width = max(1280, subject + rootPad × 2 + heroPad × 2)
```

Both paddings count. Sizing for the subject plus root padding alone silently clips it by the
width of the hero's own padding.

There is nowhere to hide metadata — frames have no `description` and plugin data is
unavailable. `ref` and `kit` are **visible Meta Rows** in `00 · Header`.

---

## Chapters

The 13 sections are grouped into 5 chapters, contiguous by number, each opened by a
`_docs/Group Header`:

```
Overview    00 – 01      Structure   02 – 06      Contract  07 – 09
Usage       10 – 11      History     12
```

Grouping is visual chunking — section numbers remain the contract. **Sections are therefore
not direct children of the root**; find them with
```js
root.findAll(n => n.type === 'FRAME'
                && /^\d\d · /.test(n.name)
                && n.parent && /^group · /.test(n.parent.name))
```

**Both the type and the parent test are required.** Figma auto-names TEXT nodes after their
own content, so a cell rendering `10 · 4` becomes a node named `10 · 4` and satisfies a bare
name regex — a real run reported 16 sections in a 13-section frame. Full rationale in
[visual-design.md](visual-design.md); the mechanism is in
[figma-api-pitfalls.md](figma-api-pitfalls.md) §19.

## Sections

Numbered so the layer panel stays ordered. Each is a VERTICAL auto-layout frame named
`NN · Title`, opened by a `_docs/Section Header` instance.

**Set each Section Header instance to `layoutSizingHorizontal = 'FILL'`.** The kit main's
width is only its own canvas size; an instance left `FIXED` stops its rule short of the
section edge, which reads as a broken layout in every section at once.

| # | Section | Required | Skip when |
|---|---|---|---|
| 00 | Header | always | — |
| 01 | Component | always | — |
| 02 | Anatomy | always | — |
| 03 | Modes | always | — |
| 04 | Variants | conditional | no variant property |
| 05 | Sizes | conditional | no size property |
| 06 | States | always | — |
| 07 | Tokens | always | — |
| 08 | Spec | always | — |
| 09 | Accessibility | always | — |
| 10 | Content | always | — |
| 11 | Do / Don't | always | — |
| 12 | Changelog | always | — |

A skipped section still gets an `_docs/Empty Section` stating **why**. A silently absent
section is indistinguishable from an oversight.

---

## 00 · Header

Identity row: component name, tag name, `_docs/Status Badge`. The component name carries
the largest type in the frame — it is the title of the document, not a section heading.

**This is the one section whose visible title is not its name.** The frame is named
`00 · Header` for the layer panel and for discovery; its `_docs/Section Header` `title` is the
**component's name** — `Tabs`, never `Header`. Following the section name literally gives a
sheet whose first heading reads "Header".
Type scale: component name 44, section title 28, subhead 20, section number 11, body 14.

Then a one-line description
— also written to the component's `description` field, which is the one durable metadata
channel available.

Then `_docs/Meta Row` × N. These are **load-bearing**, not decoration:

```
ref             48:210          ← how the skill finds the component on re-run
part set        48:396
kit             v3               ← docs-kit version this frame was built against
version         1.2.0
owner           Ada Okonkwo       ← from the Figma account, never hardcoded
last updated    2026-08-18
repo path       packages/core/src/tabs/ds-tabs.ts
code connect    not mapped
```

**`owner` is the Figma account display name**, resolved from `whoami` (`figma.currentUser`
does not exist here — figma-api-pitfalls.md §13). Never a hardcoded handle, an email local
part, or a git author. Changelog attributions use the same string, so the two cannot drift.
If identity cannot be resolved, leave it blank and flag it — a guessed owner looks
authoritative and nobody re-checks it.

**`ready-for-dev` is a gate, not a label.** Set it only when the audit returns zero
blockers.

---

## 01 · Component

**The component master itself lives here** — not an instance of it. The handoff frame is
the component's home: one place to find the thing and its documentation, and no way for
the two to drift apart or for someone to edit a master they can't see the spec for.

Move it in with `hero.appendChild(component)`. Instances elsewhere in the file are
unaffected — they reference by ID, not by location. Any superseded standalone doc frame
is renamed with the `⚠️ deprecated · ` prefix, never deleted.

Sit it on a neutral surface at 1×, with no annotations.

Below it, a **property table** — `_docs/Property Row`, one `kind=header` plus one
`kind=body` per property. Never a prose list or a formatted text blob: a table has
columns that stay aligned, cells that can be read individually, and a shape that maps
directly onto the props table in the generated docs page.

| NAME | TYPE | VALUES | DEFAULT |
|---|---|---|---|
| `state` | variant | default · hover · focus-visible · active · disabled | `default` |
| `selected` | boolean | true · false — orthogonal to state | `false` |
| `unread` | boolean | true · false — co-occurs with selected | `false` |
| `label` | text | the tab label, set per instance | `Overview` |

`name` and `default` render monospace — they are code identifiers, not prose.

### Parts

If the component has internal parts (see [sub-components.md](sub-components.md)), they live
here too — the part's component set sits in this section, beside the parent master, with a
table row each:

| NAME | NODE | STATES | WHY IT EXISTS |
|---|---|---|---|
| `Tab` | `48:396` | 5 + `selected` + `unread` | every tab in the set is an instance, each independently stateful and focusable |

Not loose on the canvas. A part set at an arbitrary coordinate is one nobody finds and
nobody keeps current. A **public** part is referenced by node id instead, and documented in
its own handoff frame.

Close with a caption naming which component the properties belong to, and pointing at
`08 · Spec` for the code-level API. When the documented component exposes no Figma
properties of its own (they live on a sub-component), say so explicitly — an empty table
and an unmentioned one look identical.

---

## 02 · Anatomy

An instance with `_docs/Callout Pin` instances **in a left gutter**, each joined to its
part by a leader line, plus a numbered legend beside the artwork.

**The pins are the whole point.** A numbered legend with no pins is a labelled list — the
numbers reference nothing and the section teaches nothing. Every legend entry must have a
matching pin anchored to the part it names. Anchor by geometry, place in the gutter — see
[visual-design.md](visual-design.md) §4b for the gutter, leader and collision rules.

Anchor each pin to a real node, computed from geometry rather than guessed:

```js
const instAbs = inst.absoluteBoundingBox;
function rel(n){                                   // node position in wrapper coordinates
  const a = n.absoluteBoundingBox;
  return { x: inst.x + (a.x - instAbs.x), y: inst.y + (a.y - instAbs.y), w: a.width, h: a.height };
}
```

Pick a **different corner per part** (`tl`, `tr`, `bl`, `br`) so pins don't stack — parts
nest, so a container and its first child often share a top-left corner. Nudge on collision:

```js
while (placed.some(p => Math.abs(p.x - x) < PIN && Math.abs(p.y - y) < PIN)) y += PIN + 4;
```

Pins are absolute-positioned inside the wrapper — the one place absolute positioning is
correct. Coordinates are **parent-relative** (figma-api-pitfalls.md §6).

**Legend labels are layer names, verbatim.** If the pin says `unread-marker`, the layer is
named `unread-marker` and the code slot will be too. That is what makes anatomy a contract
rather than decoration.

An unnamed layer in anatomy scope is a blocker.

---

## 03 · Modes

**The section that justifies the frame.** Two panels side by side, each containing the
same content, each pinned to a mode.

Panels are **plain frames**, not kit instances — a component cannot accept arbitrary
children (figma-api-pitfalls.md §2).

```js
panel.setExplicitVariableModeForCollection(semantic,  darkModeId);
panel.setExplicitVariableModeForCollection(component, componentDarkModeId);
```

Pin **every** collection that carries modes, not just Semantic — that is also what the
aliasing strategy in token-rules.md depends on.

Set the override on the panel, never on individual instances, so later additions inherit
it. More than two modes → a panel per mode. Two is the floor.

---

### What the panels must contain

The section claims that every bound variable resolves in both modes. **A panel that omits a
state does not verify that state's tokens, and the claim becomes false.** Sufficiency is not
a matter of taste:

> Each mode panel must contain at least one instance of **every token-bearing state** and
> **every size**.

A four-button panel showing one state at one size proves almost nothing while appearing to
prove everything. For a component with several axes, two blocks per panel is usually enough:
all variants across all sizes at the default state, then all states at one reference size.

### When two panels do not fit

Side by side is the default because it makes comparison immediate. It is not always
possible — two dense panels can need more width than the content column allows. **Stack them when they do not fit.** A stacked pair at full width
beats a side-by-side pair compressed to illegibility.


## 04 · Variants

One row per variant: name, live instance in each mode, and the token deltas that
distinguish it from the previous one. Names come from the Figma property values verbatim.

---

### More than two axes

"One row per variant" fails the moment a component has more than a couple of axes. A Button
with four variant axes plus two booleans runs to well over a hundred variants — that many
rows is not a table, it is a list of everything.

**Render a matrix instead:** rows are the real pairs of the two identity axes, columns are
the state combinations, at one reference size. Sizes belong to `05`, so they are not a third
dimension here.

**Absent combinations are stated, never omitted.** If only 6 of 9 `Variant × Severity` pairs
exist, the missing three get a row saying so. An omitted row and an undocumented one look
identical to a reader, and a developer will assume the full cross-product is available and
call `setProperties` toward a variant that does not exist.


## 05 · Sizes

One row per size value, showing the instance and the **resolved token values**:

```
sm   height size/24   icon size/icon/sm   padding-x spacing/8
md   height size/32   icon size/icon/md   padding-x spacing/12
```

Numbers here are rendered from resolved variables, never typed. The audit flags any row
whose text disagrees with the binding.

Note target size: WCAG 2.2
[2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum) requires 24×24.
Exactly 24 passes with no tolerance — flag it.

---

## 06 · States

A matrix: states down, modes across.

Required for anything interactive:
`default · hover · focus-visible · active · disabled`
plus whatever else exists: `loading · error · filled · selected · read-only · unread`.

**Most of those extras are not values of `state`.** Form controls are where this bites: an
invalid field can be focused and hovered, and a filled one can be anything. So `error` and
`filled` are usually booleans (`invalid`, `filled`) beside a five-value `state`, exactly like
`selected` and `unread` — rubric `F7`. A file that models them as `state` values cannot draw
an errored field with a focus ring. That is an `F7` finding to report, not a template
divergence to work around.

**Interaction states cannot be captured at rest** — render them as instances with the
state property forced. If a state is not reachable as a property, that is a blocker: an
undocumentable state is an unbuildable one.

Never use detached snapshots; they stop updating and nobody notices.

**Where two states collapse to one visual, say so.** If `selected` supersedes `unread`,
document the precedence — both remain true in data and in ARIA.

`focus-visible` is required, not optional.

---

## 07 · Tokens

The contract table — and the **RE-AUDIT baseline**. This is how the next run knows what
changed, since there is nowhere else to store it. Treat it as load-bearing.

One `_docs/Token Row` per bound property: property, component token, alias, flag, and two
live swatches carrying mode overrides.

Rows are generated from live bindings, never transcribed. Include **size, radius and
spacing** rows, not only colour — those are the ones that get hardcoded. Those rows are
`kind=value`: resolved value per mode, no swatch (docs-kit.md `_docs/Token Row`).

### When the table is too long to read

A component with a few variant axes binds the same properties once per combination, and the
table becomes most of the sheet while saying the same thing over and over. **When a table
exceeds ~25 rows and the rows follow one naming pattern** (`tabs/tab/<property>/<state>`),
collapse it the same way every time, so sheets built by different runs do not drift apart:

1. **State the pattern in prose**, naming each segment and its values.
2. **Render one group in full** as the worked example — normally the default variant.
3. **Keep every other group's header**, with its row count.
4. **Keep the collapsed rows in the frame**, in a hidden frame named `baseline · <group>`.
   This table is the RE-AUDIT baseline and `C8` compares it with live bindings, so a row
   that is merely not shown must still exist. Hidden nodes are still found by `findAll`.

Collapse only what the pattern fully explains. A row that breaks the pattern — a primitive
fallback, a hardcoded value, a token that exists for one variant only — stays visible.
Rubric `L20` raises a warning above the threshold, not a blocker: a long table is
unreadable, not wrong.

An unbound property appears as `⛔ hardcoded` and is a blocker.

---

## 08 · Spec

One **monospace** text layer containing the YAML block. See [spec-block.md](spec-block.md).

Monospace is not cosmetic here — the block is indented, structured data, and a
proportional font makes the nesting unreadable.

Resolve the font in this order, and **never create a text style**; a new style is a
type-system decision, not a documentation one:

1. An existing mono text style in the file (`/mono|code/i`) — use it.
2. Otherwise pick the first available generic mono family
   (`DM Mono`, `Fira Mono`, `Roboto Mono`, `IBM Plex Mono`, `Source Code Pro`,
   `Courier Prime`) and apply it **directly to the node**.

Detach from the proportional style first, or the style fights the override:

```js
await t.setTextStyleIdAsync('');
t.fontName = { family, style: 'Regular' };
t.fontSize = 11;
t.lineHeight = { unit: 'PIXELS', value: 17 };
```

Visually a code block; functionally the machine-readable half of the handoff.

---

## 09 · Accessibility

Rendered **from** the spec block, never written independently — two sources will disagree.

- Role and accessible-name strategy
- `_docs/Keyboard Row` per binding
- Focus model: roving tabindex vs. per-element, and where focus starts
- `_docs/Contrast Result` per pair **per mode**, alpha composited, passes included
- Link to the source: the [APG pattern](https://www.w3.org/WAI/ARIA/apg/patterns/) where one
  exists; for a native element with no APG pattern (`<select>`, `<label>`), the WHATWG HTML
  spec or the element's MDN page

---

## 10 · Content

- Labelling rules, character budget, truncation behaviour
- **Long-string example**, rendered at ~2× expected length
- **RTL example** — and whether key semantics mirror with the layout
- **Locale-derived content marked as such.** Anything from `Intl` must not be hardcoded,
  and legitimately repeated values must be labelled correct so nobody "fixes" them
- Empty / null state, if the component can receive one

---

## 11 · Do / Don't

`_docs/Guidance Card` pairs. Only mistakes actually made in this file — three earned
Don'ts beat ten hypothetical ones. Never colour alone.

---

## 12 · Changelog

Newest first, appended, never rewritten. One row per change, with the reason:

```
1.2.0  2026-08-18  unread becomes a boolean; state reduced to 5 values. Ring added —
                   tint alone fell under 3:1 and failed 1.4.11.       Design Systems Team
```

The reason is the point. A changelog of *what* without *why* is a diff, and Figma already
has one.
