# Reference: Figma API Pitfalls

Constraints in the `use_figma` environment that produce output which **looks fine and is
broken**. Every one of these was hit while piloting this skill. Read before writing.

`figma-use` has a general checklist; this file covers what specifically bites a
documentation builder.

## Find it by symptom

You will arrive here holding an error string or a screenshot, not looking for a section
number. Start here.

| Symptom | Section |
|---|---|
| `"currentUser" is not a supported API` | §13 |
| `Cannot move node. New parent is an instance or is inside of an instance` | §2 |
| `in get_name: The node with id … does not exist` | §16 |
| `in setProperties: Could not find a component property with name` | §5, §12 |
| `node.description: no such property 'description' on FRAME` | §1 |
| `Expected 'FIXED' \| 'AUTO', received 'FILL'` | §4 |
| `HUG can only be set on auto-layout frames…` | §4 |
| A frame renders **solid black** after binding a paint | §14, §7 |
| A frame is pinned at the height you passed to `resize()` | §3 |
| Rows collapsed to a sliver, text overlapping | §3, §4 |
| Text property set, canvas shows the old value | §11 |
| A variant switch wiped the text overrides | §12 |
| Instances render fine but `setProperties` fails on them | §5 |
| A marker landed outside its parent frame | §6 |
| `visible = true` had no effect | §9 |
| Content lost its variable bindings after a styling pass | §15 |
| Nowhere to store metadata on a frame | §1 |
| Quotes came back as `&quot;` from `description` | §17 |
| `x`/`y` set on a child had no effect | §18 |
| A frame you created `FIXED` is now `HUG` and growing | §3, §18 |
| A section-name regex matched something that is not a section | §19 |
| Instance counts change between calls without edits | §20 |
| A section built by resize-then-append hugs wrongly or stays pinned | §3 |
| `x.name === 'Token Row'` matches nothing, though the rows are there | §21 |
| A focus ring reports an unbound `strokeWeight`, but the panel shows it bound | §22 |
| `setBoundVariable('strokeWeight', …)` ran and nothing changed | §22 |


**Text sizing has its own reference** — see [text-layout.md](text-layout.md). §3 and §4
here are its two most frequent root causes: a text problem is usually a container problem
one or two levels up.

---

## 1. There is no hidden metadata channel

`setPluginData` and `setSharedPluginData` are **not supported** — the tool forbids them
outright. And `description` **does not exist on FRAME nodes**:

```
TypeError: node.description: no such property 'description' on FRAME node
```

`description` exists only on `COMPONENT` and `COMPONENT_SET`.

**Consequence:** the handoff frame cannot carry hidden metadata. Everything the skill
needs to find later must be either the node's **name** or **visible content**. That is
why `00 · Header` carries `ref` and `kit` as visible Meta Rows, and why `07 · Tokens`
is load-bearing for the RE-AUDIT diff.

Use component/component-set `description` where you can — it is writable, durable, and
surfaces in Dev Mode.

---

## 2. Instance subtrees are immutable — a kit component cannot be a container

```
Error: in appendChild: Cannot move node. New parent is an instance or is inside of an instance
```

You cannot append children into an instance, or into any frame nested inside one. A
`_docs/Mode Panel` component with an empty `slot` frame is unusable: the assembler can
never fill it.

**What still works inside an instance:** setting text via component properties, overriding
fills and strokes on existing children, and `setExplicitVariableModeForCollection` on a
nested node.

**Three valid patterns:**

| Need | Pattern |
|---|---|
| Container for arbitrary content | A plain **frame**, styled with the same tokens. Not a component |
| Slot for exactly one component | `INSTANCE_SWAP` property — the only slot mechanism that survives |
| Fixed content, variable text | `TEXT` component properties |

A kit component can *style* a container. It cannot *be* one.

---

## 3. `resize()` resets sizing modes — order matters

`resize()` sets `layoutSizingHorizontal` / `layoutSizingVertical` back to `FIXED`. Setting
`FILL` or `AUTO` and then resizing silently collapses the node.

```js
// WRONG — collapses to the resized height, hug is discarded
node.primaryAxisSizingMode = 'AUTO';
node.resize(880, 10);

// CORRECT — resize first, then re-enable
node.counterAxisSizingMode = 'FIXED';
node.resize(880, node.height);
node.primaryAxisSizingMode = 'AUTO';
```

Symptom: components pinned at 10px tall, content overlapping the section above.

**It is not only a text problem.** A section frame built by `resize()`-then-`appendChild`
is `FIXED` on both axes by the time its content arrives, so it stays at the resized size
instead of hugging. Set the sizing modes after the last `resize()`, for every frame you
build, and assert them in the same script.

---

## 4. `primaryAxisSizingMode` maps to a different physical axis per `layoutMode`

The single most productive source of collapsed layout. `primary` means *along the layout
direction*, not "width".

| `layoutMode` | `primaryAxisSizingMode` controls | `counterAxisSizingMode` controls |
|---|---|---|
| `HORIZONTAL` | **width** | **height** |
| `VERTICAL` | **height** | **width** |

So "fixed width, hug height" is the opposite call depending on direction:

```js
function fixedWidthHugHeight(node, width) {
  if (node.layoutMode === 'HORIZONTAL') {
    node.counterAxisSizingMode = 'AUTO';    // hug height
    node.primaryAxisSizingMode = 'FIXED';   // fixed width
    node.resize(width, node.height);
  } else {
    node.counterAxisSizingMode = 'FIXED';
    node.resize(width, node.height);
    node.primaryAxisSizingMode = 'AUTO';    // hug height
  }
}
```

Also don't cross the enums: `layoutSizing*` takes `FIXED | HUG | FILL` and is set on a
**child**; `*AxisSizingMode` takes `FIXED | AUTO` and is set on the **frame**.

---

## 5. Deleting a variant silently orphans its instances

Removing a variant from a COMPONENT_SET leaves existing instances pointing at a node that
is no longer in the set. They keep rendering the old artwork, and `setProperties` fails
with a misleading error:

```
Error: in setProperties: Could not find a component property with name: 'state'
```

The instance looks correct on canvas. It is detached from the set in every way that
matters.

**Before deleting a variant:** find every instance of the set and re-point it. **After
any variant deletion**, verify:

```js
for (const c of container.children) {
  if (c.type !== 'INSTANCE') continue;
  const main = await c.getMainComponentAsync();
  if (!main || !main.parent || main.parent.id !== setId) { /* orphan — replace it */ }
}
```

Replace an orphan by creating a fresh instance, `insertChild` at the same index, then
removing the old one. Set the **variant property first** in its own `setProperties` call —
non-variant properties do not resolve until the variant does.

---

## 6. Absolute-positioned children use parent-relative coordinates

Setting `layoutPositioning = 'ABSOLUTE'` then assigning `node.x = parent.x + offset`
places the node relative to the *parent*, not the canvas — so it lands one parent-offset
away, usually outside the frame.

```js
dot.layoutPositioning = 'ABSOLUTE';
dot.x = (parent.width - dot.width) / 2;   // parent-relative
dot.y = parent.height - dot.height - 3;
```

This is the correct way to place a marker that must not shift the content around it.

---

## 7. A stale name map produces silently unbound paints

Building `{name → variable}` and then renaming a variable leaves the map keyed on the old
name. `setBoundVariableForPaint(paint, 'color', undefined)` does not throw — it returns an
unbound paint, and the node renders **black**.

Rebuild the lookup after any rename, or bind by variable object / ID rather than by name.
Verify after binding:

```js
const bound = node.fills[0].boundVariables?.color;
if (!bound) throw new Error('unbound after binding — stale lookup?');
```

---

## 8. Fonts must be loaded before *any* mutation, including layout

The rule is broader than `characters`. `setBoundVariable('fontStyle', …)`, `appendChild`
onto a text node, and `setExplicitVariableModeForCollection` on a subtree containing text
all require every font in play to be loaded.

Load the node's **current** fonts via `getStyledTextSegments(['fontName'])` — not a
hardcoded default — plus every font you are switching to.

Applying a text style switches the font, so both the old and the new must be loaded.

---

## 9. Setting `visible` loses to a bound component property

Once `componentPropertyReferences = { visible: propId }` is set, the property's value
governs. Assigning `node.visible = true` in the same script has no effect on instances.

Set the property's **default value** when creating it; use the manual `visible` only for
the main component's own preview appearance.

---

## 10. Scripts are atomic — a failure means nothing happened

A `use_figma` script that throws makes **no** changes. There are no partial writes and no
orphans to clean up. Read the error, fix, retry — do not write defensive cleanup for a
failed call, and do not re-run "the rest" of a failed script.

---

## 11. `clone()` drops `componentPropertyReferences`

Cloning a variant to add a new one produces layers whose property references are `null`.
The set's property definitions are unchanged, `setProperties` reports success, and
`instance.componentProperties` returns the value you set — but the canvas renders the
baked characters from the clone.

Nothing throws. The data says one thing and the pixels say another.

```js
const clone = source.clone();
set.appendChild(clone);

// MANDATORY after any clone — re-point every referencing layer
const defs = Object.keys(set.componentPropertyDefinitions);
for (const [layer, prefix] of [['property','property'], ['token','token']]) {
  const t = clone.findOne(n => n.name === layer);
  if (t) t.componentPropertyReferences = { characters: defs.find(k => k.startsWith(prefix)) };
}
```

**Verify on the canvas, not in the property bag.** After setting text properties, read the
text node's `characters` and compare:

```js
const shown = instance.findOne(n => n.name === 'token').characters;
if (shown !== expected) throw new Error('property set but not rendered — broken reference');
```

This is the general lesson: `componentProperties` reports intent; `characters` reports
reality. When they disagree, the reference is broken.

---

## 12. Switching a variant drops non-variant property overrides

`setProperties({ flag: 'primitive-justified' })` swaps the underlying variant and resets
every `TEXT` / `BOOLEAN` / `INSTANCE_SWAP` override to the new variant's defaults.

Always set properties in two calls, variant first:

```js
instance.setProperties({ flag: 'primitive-justified' });   // 1. variant
instance.setProperties({ [tokenKey]: 'tabs/tab/background/unread' });  // 2. the rest
```

Same ordering rule as re-pointing an orphaned instance (§5) — non-variant properties do
not resolve until the variant does.


---

## 13. `figma.currentUser` is not available — get identity from `whoami`

```
Error: in get_currentUser: "currentUser" is not a supported API
```

There is no way to read the acting user from inside a `use_figma` script. Identity comes
from the MCP layer instead:

```
mcp__Figma__whoami  ->  { handle: "Ada Okonkwo", email: "...", plans: [...] }
```

Call it **before** the write, then pass the handle into the script as a literal. Do not
derive a name from the email, an `@`-handle, or a git author — those are different
identities and they drift apart.

If `whoami` is unavailable (headless or unauthenticated runs), leave the field **empty and
flag it**. A guessed owner is worse than a blank one: it looks authoritative and nobody
re-checks it.


---

## 14. Variable bindings set on instance children render as their literal

Assigning a bound paint to a node **inside an instance** stores the binding — and paints
the literal anyway.

```js
cap.fills = [figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', surfaceVar)];

// reads back as bound…
cap.fills[0].boundVariables.color            // -> the variable id
// …and renders solid black, because the literal is what draws
```

Six keycap chips went black this way while every check reported success: the fill was
bound, the stroke was bound, the text fill was bound *and rendered correctly*. Only the
frame fill drew its literal.

**Set variable-bound fills on the main component, not on instance children.** Text
properties override cleanly inside instances; paint bindings do not.

There is no per-node override reset — `resetOverrides()` exists only on the instance and
wipes text properties too. So when instances already carry a bad override: fix the main,
then **delete and recreate the instances**, re-applying their properties.

Two defences:

1. Pass a *sensible* base colour to `setBoundVariableForPaint`, not black. If the binding
   silently fails you get a wrong-but-plausible surface instead of a black slab.
2. Sweep chrome for unbound or literal-rendering paints after any styling pass — see
   visual-design.md §7.


---

## 15. Content lives inside the doc frame — so "everything in the frame is chrome" is false

Two earlier decisions collide:

- Parts live inside the parent's handoff frame (sub-components.md)
- A styling pass recolours everything in the handoff frame (visual-design.md)

A name-and-type heuristic walking up the tree looks sufficient and is not:

```js
// WRONG — a part SET's variants are COMPONENT nodes, not INSTANCE
if (p.type === 'INSTANCE' && p.name.startsWith('Tab')) return 'content';
```

This unbound the label fill on every `Tab` variant **and** every instance that
inherits from them, replacing tokens with a literal. Nothing threw. The frame looked
correct because the literal happened to match the light-mode value — it would have failed
in dark mode only.

**Build an explicit exempt set before styling, by identity:**

```js
const exempt = new Set();
for (const node of [documentedComponent, ...partSets, ...modePanels, ...swatches]) {
  exempt.add(node.id);
  for (const d of node.findAll(() => true)) exempt.add(d.id);
}
// then: if (exempt.has(n.id)) continue;
```

Identity, not names. Names change, types vary by whether you are looking at a set, a
variant, or an instance, and every heuristic has a case it misses.

**And verify afterwards** — count variable-bound paints inside the component before and
after. A styling pass that reduced the count damaged content.


---

## 16. Reading a node after `remove()` throws — even in the same loop iteration

```js
// identify pins by their main component, not their layer name (§21) — an instance of
// `_docs/Callout Pin` is named `_docs/Callout Pin`, so `c.name === 'Pin'` matches nothing
const isPin = async n => n.type === 'INSTANCE' && (await n.getMainComponentAsync())?.id === pinMainId;

// WRONG
for (const c of [...frame.children]) {
  if (await isPin(c)) c.remove();
  if (c.name === 'leader') c.remove();      // c is already gone
}
// Error: in get_name: The node with id "542:1280" does not exist
```

Snapshotting the children with a spread protects the *iteration*, not the *node*. Once
`remove()` is called, every property getter on that node throws — including in the very
next statement.

```js
// CORRECT — decide first, then remove and move on
for (const c of [...frame.children]) {
  const drop = (await isPin(c)) || c.name === 'leader';
  if (drop) { c.remove(); continue; }
}
```

---

## 17. `description` HTML-escapes quotes — it is not a faithful round trip

`COMPONENT.description` and `COMPONENT_SET.description` are the only durable metadata
channel available (§1), and `read-figma-component` parses them. They do **not** round trip.

```js
set.description = 'first tap shows "¿Eliminar?", second deletes';
set.description;   // 'first tap shows &quot;¿Eliminar?&quot;, second deletes'
```

Confirmed by character diff: index 316, wrote `"` (34), read back `&` (38). Newlines survive
intact; `"` does not. Assume `&`, `<` and `>` behave the same way.

Two consequences. The entity reaches anything downstream that reads the field — generated
docs, a code comment, a spec block — as literal `&quot;`. And a post-write verification that
compares strictly **reports a failure that did not happen**.

```js
// CORRECT — write typographic quotes, and normalise before comparing
const DESC = 'first tap shows “¿Eliminar?”, second deletes';
set.description = DESC;
const unesc = s => s.replace(/&quot;/g,'"').replace(/&amp;/g,'&')
                    .replace(/&lt;/g,'<').replace(/&gt;/g,'>');
if (unesc(set.description) !== DESC) throw new Error('description did not apply');
```

`descriptionMarkdown` also exists and reads as `""`. Its interaction with `description` is
unverified — do not write both.

---

## 18. Auto-layout ignores `x`/`y` — and component sets are often auto-layout with wrap

Setting `x`/`y` on a child of an auto-layout frame does nothing. The child keeps
`layoutPositioning: 'AUTO'` and Figma places it by child order. **Nothing throws.**

This bites hardest on `COMPONENT_SET`, which Figma frequently gives
`layoutMode: 'HORIZONTAL'` with `layoutWrap: 'WRAP'`. A reflow script that assigns
coordinates to every variant silently produces a wrapped flow instead — and a verification
that only checks for overlaps and bounds **passes**, because a wrapped layout has neither
problem. Only a screenshot reveals it.

Wrap also cannot produce a fixed-column grid when row widths differ: rows of narrow
variants pack more items per line than rows of wide ones.

```js
// CORRECT — check the layout mode before positioning anything
if (parent.layoutMode !== 'NONE') parent.layoutMode = 'NONE';   // then x/y apply
node.x = wantX; node.y = wantY;
const back = await figma.getNodeByIdAsync(node.id);
if (Math.abs(back.x - wantX) > 0.5) throw new Error(`x not applied: want ${wantX} got ${back.x}`);
```

See also §3: `resize()` resets sizing modes, so a frame you created `FIXED` can be found
later as `HUG`, silently growing to fit its widest child. Re-assert
`layoutSizingHorizontal` **after** every `resize()` and verify it.

---

## 19. TEXT nodes are auto-named from their content — so name regexes collide

A text node created without an explicit `name` takes its own characters as its name. A
section table that renders a padding pair as `10 · 4` produces a node named `10 · 4`, which
matches `/^\d\d · /` exactly.

On a real run this reported **16 sections in a 13-section frame**. Everything downstream
that walks sections by name then parses padding values as sections.

```js
// WRONG — matches auto-named text
root.findAll(n => /^\d\d · /.test(n.name))

// CORRECT — constrain type and parent
root.findAll(n => n.type === 'FRAME'
                && /^\d\d · /.test(n.name)
                && n.parent && /^group · /.test(n.parent.name))
```

Name every text node you create. `figma.createText()` followed by `t.name = 'value'` costs
one line and removes the whole class of collision.

---

## 20. `ComponentNode.instances` only sees loaded pages

Pages load incrementally and `loadAllPagesAsync` is unavailable here, so `instances` returns
only what is currently loaded. Across one session the same set reported three
different totals, each larger than the last — with no edits, purely as more pages were
visited.

Any instance count is a **lower bound**. Label it as one. Reporting a count as fact, to a user deciding
whether to approve a breaking change, understates the blast radius they are approving.

---

## 21. An instance of a variant is named after the component set, not the variant

A new instance takes its **component set's** name as its layer name. When the kit is
published as `_docs/Token Row`, every row instance is named `_docs/Token Row` — so an audit
that finds rows with `n.name === 'Token Row'` matches nothing, reports an empty table, and
passes every check it would have run on the rows.

```js
// WRONG — depends on the layer name, which follows the set's name and any rename
frame.findAll(n => n.type === 'INSTANCE' && n.name === 'Token Row')

// CORRECT — identify by what the instance is, not what it is called
const rows = [];
for (const n of frame.findAll(n => n.type === 'INSTANCE')) {
  const main = await n.getMainComponentAsync();
  if ((main?.parent?.type === 'COMPONENT_SET' ? main.parent : main)?.id === tokenRowSetId) rows.push(n);
}
if (rows.length === 0) throw new Error('no Token Row instances found — check the match, not the table');
```

Treat **zero matches as a failure of the query** until proven otherwise. An empty result is
the one thing an audit should never quietly accept.

---

## 22. `strokeWeight` on a RECTANGLE: bound per side, read as unbound

A RECTANGLE's stroke weight can be bound per side (`strokeTopWeight`, `strokeRightWeight`,
`strokeBottomWeight`, `strokeLeftWeight`). With all four bound, `boundVariables.strokeWeight`
**reads empty**, and `setBoundVariable('strokeWeight', v)` on the same node is a silent
no-op. A check that reads only the combined field reports an unbound focus ring on a ring
that is fully tokenised — and a fix that writes the combined field changes nothing.

```js
const SIDES = ['strokeTopWeight', 'strokeRightWeight', 'strokeBottomWeight', 'strokeLeftWeight'];
const b = node.boundVariables || {};
const bound = b.strokeWeight || (node.type === 'RECTANGLE' && SIDES.every(k => b[k]));

// binding one: write the sides on a RECTANGLE, then read them back
if (node.type === 'RECTANGLE') for (const k of SIDES) node.setBoundVariable(k, borderVar);
else node.setBoundVariable('strokeWeight', borderVar);
const back = node.boundVariables || {};
if (!(back.strokeWeight || SIDES.every(k => back[k]?.id === borderVar.id)))
  throw new Error(`${node.name}: strokeWeight not bound`);
```

Rubric `C18` reads the four sides on a RECTANGLE for exactly this reason.
