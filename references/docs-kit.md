# Reference: `_docs-kit`

Documentation is **drawn with components**, not raw shapes. Without this, every handoff
frame is an unstyleable pile of rectangles and the audit can only check that something
exists, not that it conforms.

Lives on a page named `_docs-kit`. The leading underscore sorts it to the top and marks it
as infrastructure.

---

## The container rule — read before designing any kit component

**Instance subtrees are immutable.** `appendChild` into an instance throws. A kit
component with an empty `slot` frame can never be filled by the assembler.

| Need | Build it as |
|---|---|
| Container for arbitrary content | A plain **frame**, styled with the same tokens |
| Slot for exactly one component | A component with an `INSTANCE_SWAP` property |
| Fixed structure, variable text | A component with `TEXT` properties |

A kit component can *style* a container. It cannot *be* one. This is why `Mode Panel` is
not a component, and why `Guidance Card` is caption-only.

See figma-api-pitfalls.md §2.

---

## The kit page is a deliverable too

Components dropped at arbitrary coordinates overlap, hide each other, and give no way to
see what the kit contains. Lay the page out:

```
_docs-kit  (auto-layout, page surface, 1680 wide)
├─ cover        title · one-paragraph purpose · palette swatches with hex · type scale
├─ Structure    Group Header · Section Header · Empty Section
├─ Data         Meta Row · Property Row · Token Row · Contrast Result · Keyboard Row
├─ Signals      Status Badge · Guidance Card · Callout Pin
└─ Deprecated   demoted at the bottom, reduced opacity, with the reason
```

Each component sits in a card with its **name in mono** and a one-line note on what it is
for and what constrains it. The cover documents the palette and type scale in the kit
itself, so the system is legible without reading this file.

Nothing loose on the page.

---

## The config block

**Find it by name; merge, never replace.**

```js
const config = cover.findOne(n => n.type === 'TEXT' && n.name === 'config');
```

Scanning the cover's text nodes and taking the first N will miss it on any kit whose cover
has grown — and reporting "no config block" on a kit that has one leads the write-back to
overwrite a block it never read. `severityOverrides` are decisions the user made in earlier
runs; a wholesale rewrite destroys them silently, recoverable only from Figma version
history. Read, update `lastRun` only, write back. If the block will not parse, **stop and
report** rather than replacing it.

`setPluginData` does not exist and frames have no `description`, so run state has nowhere to
hide. Put it somewhere visible instead: a text layer named `config` on the kit cover, in
YAML.

```yaml
# _docs-kit · config
kitVersion: v2
chrome: generic            # generic | system
locale: en-US
severityOverrides:
  H3: info                 # RTL example not required for this system
  G7: info
lastRun:
  component: Tabs
  node: "48:210"
  at: "2026-08-18"
  score: 84
  blockers: 0
  findings:
    - { id: C13, node: "502:8" }
    - { id: H3,  node: "523:1387" }
```

**Read it in preflight, write it at the end of every run.** Three things it buys:

1. **The questions stop repeating.** Chrome mode, kit version and locale are answered once.
2. **Severity overrides become real.** "That's deliberate for us" downgrades a check
   permanently instead of being re-argued each run.
3. **Trend comparison.** Compare this run's findings to `lastRun.findings` keyed on
   `id + node` and report the delta — *3 fixed, 1 new since 2026-08-18* — which is what
   makes repeat runs feel like progress rather than repetition.

Being visible is a feature: a designer can read it, and can edit an override without
touching the skill.

---

## Preflight

1. Page `_docs-kit` exists
2. Every component below exists, by name
3. Version on the page's cover text matches what the skill expects

| Condition | Action |
|---|---|
| Page missing | Build the kit, then continue |
| Some components missing | Build only those, report which |
| Version behind | Report the delta and offer to upgrade — never silently |
| Version ahead | Stop. A newer skill version documented this file |

---

## Type and colour: chrome is self-contained, content is not

The kit documents *any* file. A file's text styles are named however that team named them
— `Heading/Card` here, `Title/M` elsewhere, `heading-3` somewhere else — so a kit that
resolves `S['Heading/Card']` works in exactly one file and silently degrades everywhere
else. It also couples documentation chrome to product type decisions: change `Body/Small`
for a product reason and every doc frame reflows.

**Documentation chrome is infrastructure, not product UI.** Its job is legibility and
consistency across files. It gets its own type, resolved by availability:

```js
const SANS = ['Inter','Helvetica Neue','Arial','Roboto','Work Sans','IBM Plex Sans'];
const MONO = ['DM Mono','Fira Mono','Roboto Mono','IBM Plex Mono','Courier Prime'];
const sans = SANS.find(f => available(f, 'Regular'));
const mono = MONO.find(f => available(f, 'Regular'));
```

Applied directly to the node, never as a created style:

```js
await t.setTextStyleIdAsync('');            // detach, or the style fights the override
t.fontName = { family: sans, style: 'Semi Bold' };
t.fontSize = 20;
t.lineHeight = { unit: 'PIXELS', value: 28 };
t.letterSpacing = { unit: 'PERCENT', value: 0 };
```

### The scale

| Role | Family | Size | Weight | Line | Track | Used for |
|---|---|---|---|---|---|---|
| `display` | sans | 44 | Bold | 52 | −2% | Component name in `00` |
| `title` | sans | 28 | Semi Bold | 36 | −1% | Section titles |
| `subhead` | sans | 20 | Semi Bold | 28 | 0 | Sub-headings inside a section |
| `eyebrow` | sans | 11 | Semi Bold | 16 | 6% | Section numbers, mode labels |
| `bodyLg` | sans | 18 | Regular | 28 | 0 | Component description |
| `body` | sans | 14 | Regular | 20 | 0 | Prose, captions, values |
| `bodyStrong` | sans | 14 | Medium | 20 | 0 | Emphasis, ratios |
| `label` | sans | 12 | Medium | 16 | 0 | Column labels |
| `badge` | sans | 11 | Medium | 16 | 0 | Badges, flags, verdicts |
| `mono` | mono | 12 | Regular | 18 | 0 | Token paths, identifiers, defaults |
| `monoSm` | mono | 11 | Regular | 17 | 0 | Spec block, tag names, aliases |

### The boundary

**Chrome is generic. Content is the file's own.**

| Restyle | Never touch |
|---|---|
| Section headers, labels, captions, table cells, badges | The documented component and its instances |
| Prose the skill writes | Anything inside a mode panel |
| The spec block | Token swatches |

Walk up from each text node; if any ancestor is the documented component or one of its
instances, skip it. On a full 13-section frame this skips the large majority of text nodes — the component
must render in its own type, or the documentation is lying about what it looks like.

### Colour — same argument, not yet applied

Chrome colour still resolves Semantic tokens by exact name (`color/foreground/default`,
`color/border/default`, `badge/*/background`). That has the same portability problem as
type: those names are this file's, not a universal contract.

The fix is a resolver with ordered candidates and a literal fallback, so the kit renders
in a file whose tokens are named differently:

```js
function chrome(role) {                       // 'text' | 'muted' | 'border' | 'surface' | …
  for (const name of CANDIDATES[role]) if (T['Semantic:' + name]) return bind(T['Semantic:' + name]);
  return literal(FALLBACK[role]);             // neutral hex, unbound, reported as a warning
}
```

**Not implemented yet.** Until it is, the kit assumes this file's semantic names and will
need its colour bindings adjusted when ported.

---

## Kit rules

- Component **content** binds **Semantic** tokens, so it themes with the system. Chrome
  **type** is generic and self-contained — see above.
- Chrome stays legible: handoff frames render in Light. Only mode panels carry overrides.
- Auto-layout with hug sizing so content of any length fits — and mind the axis mapping:
  for `HORIZONTAL`, `primaryAxisSizingMode` is *width*, not height
  (figma-api-pitfalls.md §4). Getting this backwards collapses components to 10px.
- Text exposed as component `TEXT` properties, edited from the properties panel.
- Never instanced outside a handoff frame.
- **Column layers are `FIXED` width with `textAutoResize = 'HEIGHT'`** — never hugging.
  A hugging label collapses to its content and destroys the column alignment across rows.
  Only the last column in a row uses `FILL`.
- After `clone()`ing a variant, **re-point every layer's `componentPropertyReferences`** —
  clone drops them silently and the variant renders stale text (figma-api-pitfalls.md §11).
- **Set sizing modes AFTER `resize()`, at creation time too.** Building a component with
  `primaryAxisSizingMode` set and *then* calling `resize()` pins it at the resize height —
  every row in the table collapses to 10px. See text-layout.md → Creation order.
- Monospace: use an existing mono text style if the file has one, otherwise apply a generic
  mono family directly to the node. **Never create a text style** — that is a type-system
  decision, not a documentation one.

---

## Components

### `_docs/Section Header`
Opens every section. VERTICAL auto-layout, full width, 1px rule below bound to
`color/border/subtle`.

| Property | Type |
|---|---|
| `number` | text — `00`–`12`, mono, muted |
| `title` | text — `Heading/Card` |
| `description` | text — optional, muted |

---

### `_docs/Group Header`
| Property | Type |
|---|---|
| `label` | text — chapter name, UPPERCASE |
| `range` | text — the section numbers it covers, e.g. `02 – 06` |

A 2px rule with an uppercase label beneath it. **Deliberately not a bigger section title** —
a chapter needs a different *treatment*, not a larger size, or it reads as the same level
slightly louder. See [visual-design.md](visual-design.md) §4.

---

### `_docs/Status Badge`
| Property | Values |
|---|---|
| `status` | `draft` · `in-review` · `ready-for-dev` · `published` · `deprecated` |

Each variant carries a dot **and** a label — never colour alone
([WCAG 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)).

---

### `_docs/Callout Pin`
Numbered circle for anatomy and focus-order diagrams. Fixed 24px so pins stay consistent
across components at different scales.

| Property | Type |
|---|---|
| `number` | text |

---

### `_docs/Meta Row`
| Property | Type |
|---|---|
| `label` | text |
| `value` | text — mono for IDs and paths |

**Load-bearing.** With no plugin data and no `description` on frames, the Meta Rows in
`00 · Header` are where `ref` and `kit` live. They are the discovery contract, not
decoration.

---

### `_docs/Token Row`
| Property | Type |
|---|---|
| `property` | text — e.g. `background · selected` |
| `token` | text |
| `alias` | text |
| `flag` | variant — `none` · `semantic-gap` · `primitive-justified` · `hardcoded` |

`primitive-justified` renders **neutral**, not amber. Flagging a justified primitive as
debt trains people to ignore the column.

Two swatch nodes, `swatch-light` and `swatch-dark`. The assembler **overrides their
fills** (allowed inside an instance) and sets a mode override on each, so they are live
references rather than painted approximations.

`primitive-justified` renders neutral, not amber — it is an observation, not debt. Only
`semantic-gap` and `hardcoded` read as warnings.

Give the flag chip a **fixed height**; an empty auto-layout frame otherwise hugs to the
full row and inflates it.

---

### `_docs/Property Row`
| Property | Type |
|---|---|
| `name` | text — monospace, the code attribute name |
| `type` | text — `variant` · `boolean` · `text` · `instance-swap` |
| `values` | text — enumerated values, or a one-line note |
| `default` | text — monospace |
| `kind` | variant — `header` · `body` |

**One component for both the header and the body rows**, so the columns cannot drift
apart. `header` renders uppercase-muted with a bottom rule; `body` renders content.

Column widths are `FIXED` (`name` 220, `type` 130, `default` 140); `values` takes `FILL`.
`name` and `default` are monospace — they are code identifiers, not prose.

Replaces the prose property list. A table has columns that stay aligned and cells that can
be read individually; a formatted text blob has neither and drifts the moment a value
changes length.

---

### `_docs/Keyboard Row`
| Property | Type |
|---|---|
| `keys` | text — rendered as key caps |
| `action` | text |

---

### `_docs/Contrast Result`

> **Variants: `pass | fail | exempt | info`.** Two are not enough. The rubric depends on
> both extra states: WCAG 1.4.3 exempts inactive components, so a disabled pair measuring
> under 2:1 is *exempt*, not a failure — and a hover tint that is not the sole indicator of
> state is *info*. Rendering either as `pass` with an explanation buried in the requirement
> column is a workaround, and it makes the section's own counts wrong.
| Property | Type |
|---|---|
| `pair` | text |
| `mode` | text |
| `ratio` | text |
| `requirement` | text |
| `result` | variant — `pass` · `fail` |

One instance per pair **per mode**. Computed with alpha composited, never by eye.

---

### `_docs/Guidance Card`
| Property | Type |
|---|---|
| `caption` | text — one sentence, imperative |
| `kind` | variant — `do` · `dont` |

**One variant set, not two components.** Two near-identical components is the duplication
the kit exists to prevent.

Caption-only by design: a plain example slot cannot be filled inside an instance. If a
visual example is required, add an `INSTANCE_SWAP` property — the only slot mechanism
that survives.

Always used in pairs. Carries an icon and a label, never colour alone.

---

### `_docs/Empty Section`
Dashed placeholder for a section that is required but unfilled, or deliberately skipped.

| Property | Type |
|---|---|
| `title` | text |
| `reason` | text |

Its presence is an audit `warning` when content is expected, and an `info` when the
section is legitimately not applicable. Either way the reason is stated — a silently
absent section is indistinguishable from an oversight.

---

## Mode panels are NOT a kit component

They must accept arbitrary children, so they are plain frames the skill builds:

```js
const p = figma.createAutoLayout('VERTICAL', { name: 'mode: Dark', itemSpacing: 16 });
p.fills   = [bound('color/surface/popover')];
p.strokes = [bound('color/border/default')];
p.setExplicitVariableModeForCollection(semantic,  darkModeId);
p.setExplicitVariableModeForCollection(component, componentDarkModeId);
```

The override is what matters, and it works on any frame.

---

## Versioning

Version string on the kit page's cover text — there is no plugin data to hold it. Bump on
any structural or property-name change. On upgrade: report every handoff frame instancing
the changed components, show the property diff, wait for approval, then update the mains.

Never delete a kit component. Rename with `⚠️ deprecated · ` and set its description so
existing instances keep resolving and the reason survives.
