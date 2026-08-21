# Reference: Sub-Components (Parts)

Mid-build you realise the component has a part that needs to be a component itself — a tab
cell, a table row, a menu item. This is the most expensive discovery to make late, because
**every section of the parent's documentation depends on the part's final shape.**

On the pilot the parent was documented first. Then `Tab` was restructured
(`unread` moved from a variant value to a boolean), and sections `01 · Component`,
`06 · States` and `07 · Tokens` all had to be rebuilt. That rework is what this reference
exists to prevent.

**Resolve parts before documenting the parent. Always.**

---

## Where it sits in CREATE

```
1. Read the component set
2. PART DISCOVERY          ← here, before anything else is decided
3. Decide: extract? public or internal?
4. Build or fix the parts, and audit them
5. Only now: resolve the parent's tokens
6. …the rest of CREATE
```

Steps 2–4 are a gate. A parent whose part has blockers cannot be documented, because the
property table, the state matrix and the token table are all descriptions of the part.

---

## 1. Does this part need to be a component?

Extract when **any** of these is true:

| Trigger | Why |
|---|---|
| The part has ≥ 2 visual states | State must be a property; properties need a component |
| The part repeats ≥ 3 times | Six hand-maintained tabs is six places to drift |
| The part is independently focusable or clickable | It is a control, and controls carry state |
| Its state would otherwise be baked into parent layers | The failure this prevents — an `unread` dot hardcoded onto one specific tab |

Do **not** extract when the part appears once, has no states, and carries no interaction.
A section heading is a layer. A tab is a component.

The rubric's `F7` (orthogonal states) and `B5` (every state reachable as a property) will
force extraction anyway. Doing it here is the cheap version.

---

## 2. Public or internal?

This is the decision that determines everything downstream, and it is not about size.

**Public** — own handoff frame — when **any** of:

- It appears inside more than one parent
- A consumer could reasonably use it standalone
- It is on the component inventory or roadmap
- The code package exports it

**Internal** — documented inside the parent's frame — otherwise.

`Tab` is internal: it has states, repeats for every tab in the set, and is genuinely a control —
but it never appears outside a tab set and nobody imports it alone. Giving it its own
13-section handoff frame would be thirteen sections of noise.

### Naming encodes the decision

| | Public | Internal |
|---|---|---|
| Figma name | `Badge` | `Tab` |
| Tokens | `badge/*` | `tabs/tab/*` — namespaced under the parent |
| Code | exported `ds-badge` | private to the parent's module |
| Docs | own handoff frame | a Parts block in the parent's |

Because naming encodes it, **promotion is a breaking change**: tokens rename, the code
package gains an export, and a new handoff frame appears. Never promote silently. When an
internal part starts appearing in a second parent, report it as `info: promotion
candidate` and let a human decide.

---

## 3. Where an internal part lives

**Inside the parent's handoff frame**, in `01 · Component` → `parts`, next to the parent
master. Same rule as the parent itself (frame-template.md `01`): the documentation frame is
the component's home, so the thing and its spec cannot drift apart.

Not loose on the page. A part set sitting at some arbitrary canvas coordinate is a part
nobody will find and nobody will keep current.

### The Parts block

A `_docs/Property Row` table plus the part's component set:

| NAME | NODE | STATES | WHY IT EXISTS |
|---|---|---|---|
| `Tab` | `48:396` | 5 + `selected` + `unread` | every tab in the set is an instance, each independently stateful and focusable |

Then the set itself, so every variant is visible in one place.

---

## 4. How an internal part is documented

It does **not** get its own sections. It gets folded into the parent's, labelled by part:

| Parent section | What the part contributes |
|---|---|
| `01 · Component` | Its properties, in the property table; its master, in the Parts block |
| `02 · Anatomy` | A pin, named for the part |
| `06 · States` | Its state matrix — this is where a part's states are documented |
| `07 · Tokens` | Its tokens, under the parent's namespace |
| `08 · Spec` | A `parts:` entry (see spec-block.md) |
| `12 · Changelog` | Its changes, in the parent's log |

A public part gets all of the above **plus** its own handoff frame, and the parent's
sections reference it by node id instead of restating it.

---

## 5. Reuse before create

Before building a part, search the file for one that already exists — by name, and by
structure (same child names, same property shape). Two components called `Row` that differ
only in padding is how a library rots.

If a near-match exists, report it and ask. Never create a silent duplicate.

---

## 6. Depth

Stop at one level. A part of a part almost always means the parent is doing too much —
report it rather than recursing:

```
warning: nested part — "Tab" contains "Unread Indicator", which also has states.
         Two levels of internal parts usually means the parent should be split.
```

If the nesting is genuinely correct (a Table containing Rows containing Cells), promote the
middle layer to **public** so each level has one owner, rather than documenting three
levels inside one frame.

---

## 7. Rollup

A parent is only as ready as its parts.

- `ready-for-dev` on the parent requires **zero blockers on every part**
- A part's blockers appear in the parent's report, attributed:
  `blocker · part "Tab" · F7 — unread is a variant value`
- The parent's `08 · Spec` records each part and whether it is public, so
  `build-figma-component` knows whether to emit a package export or a private class

---

## 8. What to do when you discover a part mid-build

You will, sometimes, despite step 2. When it happens:

1. **Stop documenting.** Do not finish the section you are on.
2. Report what you found and which sections it invalidates — usually `01`, `06`, `07`.
3. Resolve the part: extract, decide public/internal, build, audit clean.
4. Re-run the parent's affected sections.
5. Add a changelog row saying the part was extracted and why.

Finishing the parent's documentation first and patching afterwards costs more than
stopping, every time. It also produces a frame that is briefly, invisibly wrong — which is
worse than one that is obviously unfinished.
