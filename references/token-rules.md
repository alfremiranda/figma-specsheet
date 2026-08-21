# Reference: Token Rules & Mode Strategy

---

## The tier model

```
Primitives   raw values          color/cyan/700 = #0E7490
     ↑ alias
Semantic     purpose + theming   color/interactive/primary   [Light | Dark]
     ↑ alias
Component    component contract  tabs/tab/background/selected
```

Each tier aliases the one above. **No tier stores a raw value except Primitives.**

---

## Rule zero: match the file

Before creating anything, read how the file already does it:

```js
const probes = ['button/filled/background/default', 'input/color/background'];
// → naming shape, which tier they alias, scopes, mode usage
```

Three things you are looking for:

1. **Naming shape.** `{component}/{part}/{property}/{state}` at collection root, or
   `component/{name}/…`? Follow what's there.
2. **Which tier existing component tokens alias.** If they go straight to Primitives,
   understand why before diverging.
3. **How many modes the Component collection has**, and whether frames pin Semantic and
   Component modes *together*. That last one decides the aliasing strategy below.

Deviate only where provably safe — setting explicit `scopes` when the file uses
`ALL_SCOPES` is safe, because scopes do not affect resolution. Say so in the report.

---

## Where modes live

**If the Component collection is single-mode:** alias Semantic. Light/dark resolve through
it automatically. Nothing more to do.

**If the Component collection is multi-mode** (common in mature files), you have a choice,
and it depends on one fact: *does the file pin Semantic and Component modes together on
the same frame?*

```js
frame.explicitVariableModes  // → { Semantic: 'Dark', Component: 'dark' }
```

- **Pinned together** → set the **same Semantic alias in every Component mode**. Mode
  parity is satisfied, and theming stays a single decision made once in Semantic. These
  tokens inherit any future retheme for free.
- **Pinned independently** → alias Primitives per mode, like the file's existing tokens.
  Aliasing Semantic would resolve against whichever Semantic mode happens to be active
  and produce wrong colours.

Check before choosing. Do not assume.

Never give the Component collection new modes to express theming that Semantic already
expresses. That duplicates the decision and drifts.

### Rendering both modes

Modes are proven by rendering, not asserted:

```js
panel.setExplicitVariableModeForCollection(semantic, darkModeId);
panel.setExplicitVariableModeForCollection(component, componentDarkModeId);
```

Set the override on the **panel frame**, never on individual instances, so anything added
later inherits it. The panel must be a frame — see figma-api-pitfalls.md §2.

---

## Two axes: source, then tier

Resolution has **two** dimensions, and only one of them is about tiers.

### Source — checked first

| # | Source | Why |
|---|---|---|
| 1 | **Published library variable** | The shared contract. Always prefer it |
| 2 | Local variable | This file's own |
| 3 | Local style | Legacy; a paint style where a variable should be |
| 4 | Nothing | **Stop and report** |

In a file that consumes a published design system, binding a *local* variable that
duplicates a published one silently detaches that node from the library. It looks correct —
same colour, same name — and it stops receiving updates.

```js
const published = await figma.variables.getVariableByIdAsync(importedId);   // library
const local     = localVars.find(v => v.name === name);                     // this file
// prefer `published`; if `local` duplicates it by name and resolved value, that is a finding
```

**A local variable whose name and resolved value match a published one is a duplicate** —
warning `C17`, naming the library variable it shadows.

### Tier — checked within the chosen source

Stop at the first hit.

| # | Try | On hit | On miss |
|---|---|---|---|
| 1 | Existing component token | Reuse. Never duplicate | → 2 |
| 2 | Semantic token matching **intent**, then value | Alias it | → 3 |
| 3 | Primitive matching the exact value | Alias it, then classify (below) | → 4 |
| 4 | Nothing matches | **STOP.** `needsHumanReview` | — |

**Intent beats value.** If a border happens to equal `color/border/subtle` but semantically
it is a focus ring, alias `color/border/focus` — creating it first if needed. Matching on
hex produces tokens that are right today and wrong after the first rebrand.

Step 4 is a hard stop. Rounding `#2563EA` to the nearest primitive silently changes the
design and destroys the audit trail.

### Classifying a Primitive alias

Not every skipped Semantic is a gap. Two codes:

| Code | Meaning | Severity |
|---|---|---|
| `semantic-gap` | A semantic token *should* exist for this intent | warning |
| `primitive-justified` | No purpose-level meaning worth naming | info |

`primitive-justified` covers alpha tints, one-off decorative values, and anything whose
"meaning" is just its arithmetic. Example:

```
tabs/tab/background/unread → color/blue/500/30
```

A 30% alpha tint has no purpose-level meaning worth a semantic token, and it composites
correctly against any surface, which is why one value serves both modes.

**`primitive-justified` requires a written reason in the variable's description.** Without
that requirement it becomes an escape hatch and the warning stops meaning anything.

---

## Naming grammar

Match the file first. Absent a convention:

```
{component}/{part}/{property}/{state}
```

- `component` — kebab-case, no `ds-` prefix
- `part` — the anatomy layer it styles: `tab`, `indicator`, `item`
- `property` — from the closed list below
- `state` — `default · hover · focus · active · selected · disabled · read-only`

**Omit any segment that does not vary.** Redundant segments read as meaning later.

### Property vocabulary (closed)

| Property | For | Scopes |
|---|---|---|
| `background` | fills | `FRAME_FILL`, `SHAPE_FILL` |
| `foreground` | text colour | `TEXT_FILL` |
| `icon` | icon colour | `SHAPE_FILL`, `STROKE_COLOR` |
| `border` | stroke colour | `STROKE_COLOR` |
| `indicator` | a marker that is not a border or a fill — dot, bar, badge | `SHAPE_FILL`, `FRAME_FILL` |
| `border-width` / `ring-width` | stroke weight | `STROKE_FLOAT` |
| `ring` | focus ring colour | `STROKE_COLOR`, `EFFECT_COLOR` |
| `radius` | corner radius | `CORNER_RADIUS` |
| `height` / `min-width` / `icon-size` | dimensions | `WIDTH_HEIGHT` |
| `padding-x` / `padding-y` / `gap` | spacing | `GAP` |
| `shadow` | elevation | `EFFECT_FLOAT`, `EFFECT_COLOR` |
| `opacity` | opacity | `OPACITY` |
| `duration` | transition | `ALL_SCOPES` (no dedicated scope exists) |

Anything outside this list needs a decision before it needs a token.

### The name must match the binding

A token named `…/border/unread` bound to a **fill** is lying. When a treatment changes —
ring becomes a dot becomes a filled circle — **rename the token in the same change**.

Audit check `C13` enforces this: the `property` segment must match the node property the
token is actually bound to. `C14` catches the matching failure in prose — a description
still describing a treatment two revisions old.

### Scopes are mandatory

```js
const v = figma.variables.createVariable(name, componentCollection, 'COLOR');
v.scopes = ['FRAME_FILL', 'SHAPE_FILL'];
v.setValueForMode(modeId, { type: 'VARIABLE_ALIAS', id: target.id });
v.description = 'Why this token exists, and what it measured.';
```

Default `ALL_SCOPES` puts every component token in every picker in the file. At a few
hundred tokens the picker becomes unusable and designers go back to hardcoding — the exact
failure this system exists to prevent.

---

## Size, radius and spacing are tokens too

The most common miss. Preflight must inventory **FLOAT and STRING** variables, not just
COLOR — otherwise you hardcode `32` and `radius 6` while `size/32` and `radius/full`
already exist in Semantic.

Bind them:

```js
node.setBoundVariable('height', T['Semantic:size/32']);
node.setBoundVariable('topLeftRadius', T['Semantic:radius/full']);   // all four corners
```

Style Dictionary emits these unitless, so components wrap them:

```css
--_tab-h: calc(var(--semantic-size-32, 32) * 1px);
```

---

## Typography — two valid strategies, one per node

| Strategy | Use when | How |
|---|---|---|
| **Text style** | The whole ramp is fixed for the component | `await node.setTextStyleIdAsync(id)` |
| **Typography variables** | A single axis varies by state | Bind `fontFamily`, `fontStyle`, `fontSize`, `lineHeight`, `letterSpacing` individually |

Variables are the right call when, say, `selected` needs `weight/Medium` while every other
state stays `weight/Regular`. Inventing a second text style for a one-axis difference is
worse.

**Never mix the two on one node** — that is the actual failure mode, not the choice
itself. Record which strategy is in use in the spec block so the code side knows whether
to emit a class or individual properties.

If no text style and no typography variable matches, **stop**. Creating either is a
typography-system decision, not a component decision.

---

## Mode parity

Every variable in every collection the component touches must resolve in **every** mode.
Figma does not require this; a missing value falls back silently.

```js
const missing = collection.modes
  .filter(m => variable.valuesByMode[m.modeId] === undefined)
  .map(m => m.name);
```

Any result is a **blocker**. Walk the whole chain — Component → Semantic → Primitives. A
gap three levels up still breaks the component.

---

## Contrast gates — composite alpha first

**This is the check that most often reports a false pass.**

Resolve the alias chain to a concrete value per mode, **composite any alpha against the
actual backdrop**, and only then compute the ratio:

```js
function over(fg, bg) {
  const a = fg.a === undefined ? 1 : fg.a;
  return { r: a*fg.r + (1-a)*bg.r, g: a*fg.g + (1-a)*bg.g, b: a*fg.b + (1-a)*bg.b };
}
```

Reading raw RGB on a 20 %-alpha white token reports a ratio in the teens where the
composited value is under 2:1 — an invisible focus indicator passing the audit. Any token built on an alpha
primitive is mis-scored without this.

The backdrop is the resolved surface token, not white.

| Pair | Requirement | Source |
|---|---|---|
| Text on its background | 4.5:1 | [WCAG 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum) |
| Large text (≥24px, or ≥18.66px bold) | 3:1 | 1.4.3 |
| Any element identifying a **state** | 3:1 | [WCAG 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast) |
| Focus ring vs. **both** neighbours | 3:1 | 1.4.11 |
| Disabled text | exempt — report the ratio | 1.4.3 |

Three things people get wrong:

1. **A tint that marks a state is not decoration.** If it is the only thing distinguishing
   the state, it needs 3:1. If it fails, add a second cue that passes — a ring, a weight
   change — rather than deepening the tint until it collides with another state.
2. **Focus rings are measured against both neighbours** — the component background *and*
   the surface behind it.
3. **Transient states are different.** Hover is accompanied by a cursor and is not the
   sole means of identifying a component; report the ratio as `info`, don't fail it.

Log every check to `_docs/Contrast Result`, passes included. A visible pass is evidence;
an absent check is ambiguity.

---

## Promotion and over-abstraction

Same alias target used by ≥2 components with the same intent → a semantic token wants to
exist. Always `info`, never automatic — it is a breaking change to both components.

The inverse: a component token used by exactly one component, aliasing a semantic token
used nowhere else, is indirection for its own sake. Also `info`.
