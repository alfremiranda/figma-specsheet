# Reference: Post-Write Verification

**Every write script ends by verifying its own returned node IDs, and throws if any check
fails.** Not at the end of the phase — at the end of the write.

This is the single highest-value rule in the skill, and it was earned. Every failure below
came from a script that returned success with valid node IDs:

| Failure | Actually caught | Should have been |
|---|---|---|
| A styling pass unbound the content paints | Two calls later, by chance | Same script |
| Six key caps rendered solid black | Next screenshot | Same script |
| A cloned variant rendered stale text | Next screenshot | Same script |
| Labels wrapped per character | Only when a human looked | Same script |

In each case the information needed to catch it was already in scope at write time. Nothing
was missing except the assertion.

---

## Why throwing is correct

`use_figma` is **atomic** — a thrown error means the script did not execute and the file is
untouched (figma-api-pitfalls.md §10). So a failed assertion is free: no partial state, no
cleanup, and the agent reads the reason instead of building on a broken foundation.

Returning a warning instead would leave the damage in place and let the next call compound
it. Throw.

```js
// ... the write ...
const failures = verify(mutated);
if (failures.length) throw new Error('post-write verification failed: ' + JSON.stringify(failures, null, 2));
return { mutatedNodeIds: mutated.map(m => m.id), verified: failures.length === 0 };
```

---

## The standard assertions

Assert only what the script claimed to do. A write that bound paints asserts bindings; it
does not need to assert text.

### Every write

| Assert | Why |
|---|---|
| Every returned ID resolves via `getNodeByIdAsync` | A removed or replaced node returns null |
| No node has `width < 1` or `height < 1` | The collapse signature |

### After binding a paint

```js
const bound = node.fills[0]?.boundVariables?.color;
if (!bound) throw new Error(`${node.name}: paint not bound`);
if (bound.id !== expectedVariableId) throw new Error(`${node.name}: bound to the wrong variable`);
```

Catches the stale name→variable map (§7) and the instance-child override that stores a
binding and paints the literal (§14).

### After setting text properties

```js
const shown = instance.findOne(n => n.name === layer).characters;
if (shown !== expected) throw new Error(`${layer}: property set but not rendered`);
```

`componentProperties` reports intent; `characters` reports reality. A cloned variant with
dropped references satisfies the first and fails the second (§11).

### After creating or resizing a frame

```js
if (frame.layoutMode === 'HORIZONTAL' && frame.counterAxisSizingMode !== 'AUTO')
  throw new Error(`${frame.name}: height will not hug`);
if (frame.layoutWrap === 'WRAP' && frame.layoutSizingHorizontal === 'HUG')
  throw new Error(`${frame.name}: wrap is on but width hugs — it will grow, not wrap`);
const p = frame.parent, inner = p.width - (p.paddingLeft || 0) - (p.paddingRight || 0);
if (frame.width > inner + 0.5)
  throw new Error(`${frame.name}: ${Math.round(frame.width)} wide in a ${Math.round(inner)} column`);
for (const t of frame.findAll(n => n.type === 'TEXT')) {
  const lh = lineHeightOf(t);
  if (t.textAutoResize === 'HEIGHT' && t.height > lh * 1.6 && t.characters.length < 24)
    throw new Error(`${t.name}: short string wrapping at w ${Math.round(t.width)}`);
}
```

Catches `resize()`-after-sizing (§3), starved `FILL` text, a wrap that cannot wrap, and a
frame wider than the column it sits in (text-layout.md · containment).

### After deleting a variant

```js
for (const c of container.children) {
  if (c.type !== 'INSTANCE') continue;
  const main = await c.getMainComponentAsync();
  if (!main || main.parent?.id !== setId) throw new Error(`orphaned instance ${c.id}`);
}
```

Deleting a variant orphans its instances silently — they keep rendering (§5).

### After any styling pass

```js
let bound = 0;
for (const n of [component, ...partSets]) for (const d of [n, ...n.findAll(() => true)])
  for (const p of (Array.isArray(d.fills) ? d.fills : [])) if (p.boundVariables?.color) bound++;
if (bound < boundBefore) throw new Error(`styling pass unbound ${boundBefore - bound} content paints`);
```

Count before, count after. A drop means the pass reached into content (§15). **Take the
"before" count in the same script**, not from memory.

---

## The one exception

A **discovery** script — read-only, returning data — has nothing to verify. Everything that
mutates verifies.

---

## Relationship to the audit rubric

Post-write verification and the rubric check overlapping things at different times, and both
are needed:

| | Post-write | Rubric |
|---|---|---|
| When | Inside the write | End of run |
| Scope | What this script touched | The whole frame |
| On failure | Throws, file untouched | Reports, human decides |
| Catches | Damage at the moment it happens | Gaps, drift, missing sections |

`A12`, `C15` and `L9` exist in the rubric because they were learned late. Keep them — a
frame edited by hand between runs still needs them — but they should almost never fire once
post-write verification is in place. **If a rubric blocker fires for something a write
should have caught, the write's assertions were incomplete. Fix the assertion, not just the
node.**

---

## Assert the value you asked for, not merely a self-consistent result

The rule above proves a write *happened*. It does not prove the write produced **what you
intended**, and those are different things.

A reflow assigned `x`/`y` to every variant of a large `COMPONENT_SET` that had
`layoutWrap: 'WRAP'`. Auto-layout ignored every coordinate. The verification checked that no
two nodes overlapped and that all were inside the parent — and **passed**, because a wrapped
flow satisfies both. The grid was completely wrong and only a screenshot showed it.

```js
// INSUFFICIENT — a wrapped auto-layout passes this
if (overlaps(a, b)) fail();
if (outOfBounds(n, parent)) fail();

// REQUIRED — compare against the intended value
const want = intended.get(n.id);
const back = await figma.getNodeByIdAsync(n.id);
if (Math.abs(back.x - want.x) > 0.5 || Math.abs(back.y - want.y) > 0.5)
  fail({ id: n.id, want: [want.x, want.y], got: [back.x, back.y] });
```

Build the `intended` map as you write, then verify against it. Any check that could pass on
a result you did not ask for is not a verification, it is a sanity check.

### Corollaries

- **Check `layoutMode` before positioning.** If it is not `NONE`, coordinates are ignored
  (§18).
- **Re-assert sizing modes after `resize()`.** A root frame created `FIXED` was later found
  `HUG`, silently growing to fit its widest child (§3). Set the mode, resize, set it again,
  then verify it reads back as intended.
- **Normalise before comparing text.** `description` HTML-escapes quotes, so a strict
  comparison reports a failure that did not occur (§17).
- **Do not invent the assertion's own threshold.** A "starved text" check keyed on raw width
  flagged dozens of correctly-designed fixed-width label columns. An over-eager assertion trains
  the reader to ignore the output — the same failure mode as an over-eager sweep.

## One compositing helper, used everywhere

Alpha compositing is written once and imported, never re-implemented per call site.

On a single run the correct composited value was computed for a report, and then the same
maths was rewritten minutes later inside a solver — dropping the alpha. The solver reported
that a token needed fixing in Dark when the properly composited measurement passed
comfortably. The rule that exists to prevent exactly this error was broken by re-typing it.

```js
const over = (fg, bg) => ({
  r: fg.r*fg.a + bg.r*(1-fg.a),
  g: fg.g*fg.a + bg.g*(1-fg.a),
  b: fg.b*fg.a + bg.b*(1-fg.a), a: 1
});
```

Every ratio in a run comes from that one function. If a script computes a contrast number
without calling it, the number is wrong.

