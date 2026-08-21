# Reference: `08 · Spec` Block Schema

One monospace text layer inside a section named `08 · Spec`. Valid YAML.

This is the half of the handoff Figma cannot express. Everything here is a decision a
human made; nothing is inferred from the canvas. It exists so `read-figma-component` reads
facts instead of guessing — its `Role not determinable from Figma` flag should never fire
on a component with a valid spec block.

---

## Schema

```yaml
# ---- identity ----
component: ds-tabs
figmaNode: "48:210"
partSet: "48:396"            # the sub-component set, if the component has one
version: 1.2.0
status: in-review             # draft | in-review | ready-for-dev | published | deprecated
owner: Design Systems Team

# ---- props: Figma names ARE the code attribute names ----
props:
  - name: value
    type: string
    note: id of the selected tab
    default: null
  - name: orientation
    type: string
    values: [horizontal, vertical]
    default: horizontal
  - name: activation
    type: string
    values: [automatic, manual]
    default: automatic
    note: manual means arrow keys move focus without selecting; Enter or Space commits.

# ---- parts: sub-components this one owns ----
# public: false  -> a private class inside the parent's module, no package export
# public: true   -> its own export, and its own handoff frame
parts:
  - name: Tab
    figmaNode: "48:396"
    public: false
    reason: every tab in the set is an instance, each independently stateful and focusable.
    tokenNamespace: tabs/tab/*

# ---- orthogonal state model ----
# Anything that can co-occur is its OWN property, never a value of one variant.
stateModel:
  variant:
    name: state
    values: [default, hover, focus-visible, active, disabled]
  booleans:
    - name: selected
      note: The active tab. Co-occurs with hover and focus-visible.
    - name: unread
      note: Indicator dot. Co-occurs with selected — a tab can be current AND have new content.
  precedence:
    - when: unread AND selected
      renders: both
      note: The dot persists on the selected tab. Suppressing it loses the only signal
            that content changed while the tab was open.

# ---- typography: state ONE strategy ----
typography:
  strategy: typography-variables      # or: text-style
  bindings:
    fontFamily: font-family
    fontStyle: weight/Regular         # weight/Medium on selected
    fontSize: size/14
    lineHeight: leading/20
    letterSpacing: tracking/normal
  note: Variables rather than a text style, so weight varies by state without a second style.

# ---- accessibility: from the APG pattern, not from memory ----
a11y:
  pattern: https://www.w3.org/WAI/ARIA/apg/patterns/tabs/
  role: tablist
  accessibleName: aria-label on the tablist, naming what the set of tabs switches between.
  requiredAttrs:
    - role="tab" on each tab, role="tabpanel" on each panel
    - aria-selected on the selected tab, false on the others
    - aria-controls on each tab, pointing at its panel id
    - aria-disabled on unavailable tabs
  keyboard:
    - keys: Arrow Left / Right
      action: Previous / next tab (Up / Down when orientation is vertical)
    - keys: Home, End
      action: First / last tab
    - keys: Enter, Space
      action: Select the focused tab — only when activation is manual
  focus:
    model: roving-tabindex
    initial: selected tab, else first enabled tab
    note: The tablist is ONE tab stop, not one per tab.
  targetSize: 44
  reducedMotion: Indicator slide disabled under prefers-reduced-motion.

# ---- events consumed by the React wrapper via addEventListener ----
events:
  - name: ds-change
    detail: "{ value: string }"
    when: A tab is selected

# ---- behaviour Figma cannot show ----
behavior:
  - Panels stay mounted when hidden, so scroll position and form state survive switching.
  - Overflowing tabs scroll horizontally; they never wrap to a second row.
  - The selected indicator animates between tabs, not per tab — one element, translated.

# ---- content ----
content:
  note: Labels truncate at the tab's max width with a tooltip carrying the full string.
        Never abbreviate in the label itself.
  rtl: Order mirrors, and arrow-key semantics mirror with it.

# ---- links ----
links:
  storybook: https://…/?path=/story/tabs
  docs: https://…/components/tabs
  source: packages/core/src/tabs/ds-tabs.ts
  codeConnect: not mapped

# ---- known gaps: honesty beats a clean-looking spec ----
flags:
  - severity: info
    code: primitive-justified
    detail: tabs/tab/background/unread aliases color/blue/500/30 — no semantic equivalent should exist.
```

---

## Validation

Before writing:

- YAML parses
- `props[].name` matches the Figma property names exactly
- `parts[]` lists every sub-component, each with an explicit `public` flag
- `stateModel.booleans` covers every state that can co-occur with another
- `precedence` is stated wherever two true states collapse to one visual
- `a11y.pattern` is a real APG URL and `a11y.role` is that pattern's role
- `keyboard` is non-empty for anything interactive
- `typography.strategy` is one of the two valid values, and the bindings match it
- `flags` mirrors the current audit — a stale `flags` block is worse than none

Do not write a partial block. Report and stop.

---

## Why `stateModel`, `behavior` and `flags` matter most

Everything else could in principle be derived from the canvas. These three cannot.

`stateModel` is the one that prevents rework. Discovering after documentation that two
states co-occur means redoing the variant set, the state matrix, the token table and the
generated enum.

`behavior` is the portalling, the timing, the focus return — the reasons a Dialog takes
a week and a Badge takes an hour. It turns a vague `Complex interaction` flag into a brief.

`flags` is the debt ledger. A spec that lists its own gaps is trustworthy; one that looks
perfect is either finished or hiding something, and the reader cannot tell which.
