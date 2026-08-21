# Reference: Audit Rubric

Dry run by default. Nothing written without `--apply` or explicit approval.

## Find the check by symptom

| Symptom | Check |
|---|---|
| A state can't be selected in the properties panel | `B5` |
| Two states are true at once and only one renders | `F7`, `F8` |
| Dark mode looks wrong but light is fine | `D4`, `E1`–`E4` |
| A focus ring is invisible | `E3`, `E4` |
| A token name no longer describes what it does | `C13`, `C14` |
| A colour renders but isn't themed | `C1`, `C15` |
| A local token shadows a published one | `C17` |
| A section is missing and nobody knows why | `A4`, `A5` |
| The handoff frame can't be found on re-run | `A1`, `A8` |
| An instance renders but won't take properties | `A9` |
| Text wraps or clips | `J1`–`J8` |
| A card is invisible against the page | `L4` |
| Documentation restyled the component it documents | `L9`, `A17` |


| Severity | Meaning | Effect |
|---|---|---|
| `blocker` | The component cannot be built correctly from this frame | `needsHumanReview` non-empty |
| `warning` | Buildable, carries debt or will drift | Reported |
| `info` | Observation or opportunity | Reported |

---

## Ø · What changed (RE-AUDIT only — runs first)

Diff the component against the last documented state, recorded in `07 · Tokens` and
`00 · Header`. Emit a change table **before** any findings. A designer's change is not a
finding; only its consequences are.

Detect: bindings added/removed/retargeted, variant options added/removed, properties
added/removed or retyped, structural changes per variant, size/radius/typography
rebindings, token renames.

---

## A · Structure

| Check | Sev | Detail |
|---|---|---|
| A1 Handoff frame found by name | blocker | No plugin data exists — names are the contract. On miss, search the page and offer "did you mean", never silently CREATE a duplicate |
| A2 All required sections present | warning | One per missing section |
| A3 Sections in numbered order | info | Layer panel only |
| A4 Skipped section states a reason | warning | Silence is indistinguishable from oversight — use `_docs/Empty Section` |
| A5 No `_docs/Empty Section` left where content is expected | warning | Names the section |
| A6 No detached instances | warning | Detached content stops updating |
| A7 Unmanaged nodes retained | info | Designer additions — kept, listed |
| A8 `ref` in `00 · Header` still resolves | blocker | Frame is orphaned from its component |
| A9 **No orphaned instances** | blocker | Every instance's `getMainComponentAsync().parent` is the live set. Deleting a variant orphans instances silently — they keep rendering and fail `setProperties` |
| A10 Component master lives inside the handoff frame | warning | `01 · Component` holds the master, not an instance. A master outside its own documentation drifts from it |
| A11 Section headers span their section | warning | An instance left `FIXED` stops its rule short of the edge — cosmetic, but it fails in all 13 sections at once |
| A12 **Rendered text matches the property value** | blocker | `componentProperties` reports intent; `node.characters` reports reality. A cloned variant with dropped references satisfies the first and fails the second |
| A13 **Every legend entry has an anchored pin** | blocker | A numbered legend with zero pins is a labelled list — the numbers reference nothing. Every entry needs a pin anchored to the part it names, by geometry rather than by guess. Where the pin sits is `L15` |
| A14 **Sections resolve by type and parent, not by name alone** | blocker | `findAll` on a bare `/^\d\d · /` also matches auto-named TEXT nodes. Assert the count equals the number of section frames; a mismatch means something downstream will parse a table cell as a section |
| A15 **Content width was fixed before the first section** | warning | Every table is laid out against it. If the visual pass moves it afterwards, they all overflow |
| A14 Properties render as a table, not prose | warning | `_docs/Property Row`, header + one body row per property |
| A15 Spec block is monospace | warning | Existing mono style if the file has one, else a generic mono family applied to the node. Never create a style |
| A16 **Docs chrome uses no file text styles** | warning | Every chrome text node has `textStyleId === ''` and a family from the generic scale. A kit bound to one file's style names works in one file |
| A17 Documented component keeps its own type | blocker | The restyle sweep must skip the component and its instances. Documentation that restyles its subject is lying about it |

---

## B · Component contract

| Check | Sev | Detail |
|---|---|---|
| B1 Property names lowercase kebab-case | warning | Renaming is **breaking** — diff + instance count first |
| B2 Property values lowercase | warning | |
| B3 Every layer in anatomy scope is named | blocker | `Rectangle 4` cannot become a code slot |
| B4 Component set has a description | warning | The only durable metadata channel available |
| B5 Every state reachable as a property | blocker | An undocumentable state is an unbuildable state |
| B6 No orphan variant combinations | warning | Lists gaps |
| B7 Booleans named without `is`/`has` | info | `disabled`, not `isDisabled` |
| B8 Variant structure consistent across variants | warning | A layer present in 5 of 6 variants breaks instance-swap matching. Vestigial layers from a previous treatment are the usual cause |

---

## C · Tokens

| Check | Sev | Detail |
|---|---|---|
| C1 Every visual property bound | blocker | Includes **size, radius, spacing** — not just colour |
| C2 Component tokens are aliases only | blocker | Raw value in the Component collection |
| C3 Naming grammar conforms | warning | Against the file's convention first, the closed vocabulary second |
| C4 `scopes` set explicitly | warning | Picker pollution |
| C5 Alias resolves to Semantic | — | Clean |
| C6a Alias resolves to Primitive, no reason given | warning | `semantic-gap` — names the token that should exist |
| C6b Alias resolves to Primitive with a written reason | info | `primitive-justified` |
| C7 Alias chain unbroken | blocker | Deleted link mid-chain |
| C8 Section 07 rows match live bindings | blocker | Transcribed table has drifted |
| C9 Orphan component tokens | warning | Deprecate, never delete |
| C10 Promotion candidates | info | Same target, ≥2 components |
| C11 Single-use indirection | info | Over-abstraction |
| C12 New variables not yet published | warning | `action required: publish library` |
| C13 **Token name matches its binding** | warning | The `property` segment (`background`/`border`/`indicator`/…) must match the node property it is bound to. A `…/border/unread` bound to a fill is lying |
| C14 **Description is not stale** | warning | Flag any description naming a treatment (`ring`, `dot`, `border`, `pill`, `underline`) that contradicts its current binding |
| C18 **`strokeWeight` and `opacity` are bound, not literals** | warning | `C1` covers fills, sizes and radii but missed stroke weight. A 1px border and a 2px focus ring are visual values like any other. If the system has no `size/border/*` scale, that is the finding — report the gap, do not silently hardcode. **`opacity` is the one that hides**: a disabled variant dimmed by an unbound opacity looks tokenised because every fill beside it is bound, and `C1` never inspects it |
| C16 **Published library variable preferred over a local one** | blocker | Binding a local duplicate silently detaches the node from the library |
| C17 **No local variable shadows a published one** | warning | Same name and resolved value as a library variable — names the one it shadows |
| C15 Bound paint is actually bound | blocker | A stale name→variable map yields an unbound black paint without throwing. Verify `fills[0].boundVariables?.color` after binding |

---

## D · Modes

| Check | Sev | Detail |
|---|---|---|
| D1 Semantic has ≥2 modes | blocker | Precondition |
| D2 Section 03 renders every mode | blocker | Two is the floor |
| D3 Override on the panel frame, not instances | warning | Later additions won't inherit |
| D4 Mode parity across the whole alias chain | blocker | The silent killer |
| D5 Aliasing strategy matches how the file pins modes | blocker | Semantic aliases in a multi-mode Component collection are only correct if frames pin both together |
| D6 Component-collection modes not duplicating Semantic theming | warning | Unless documented |

---

## E · Contrast — per mode, alpha composited

| Check | Sev | Detail |
|---|---|---|
| E0 **Alpha composited before the ratio, by one shared helper** | blocker (of the audit itself) | Raw RGB on an alpha token reports a pass where there is a failure. If E0 is not implemented, every E result is void. **Written once and reused** — re-implementing the maths per call site is how the alpha gets dropped, and it has happened inside a single run: the correct composited value was computed for a report, then the same maths retyped in a solver returned a wrong verdict |
| E1 Text vs background ≥ 4.5:1 (3:1 large) | blocker | Per mode, per variant, per state |
| E2 Any element identifying a **state** ≥ 3:1 | blocker | A tint that is the sole marker of a state counts |
| E3 **Focus indicator ≥ 3:1 against the layer it touches** | blocker | *Adjacent*, not "vs the background". For a two-tone ring the meaningful pair is inner-vs-halo. Measuring an inner ring against a canvas it never touches produces a very different number from measuring it against the halo it does touch — wrong in both directions, and by a wide margin |
| E4 Every layer of the indicator identified before measuring | blocker | Read the effect stack and its bound variables first. A halo whose colour matches the canvas is a *gap*, not a second ring, and holding it to 3:1 invents a requirement that does not exist |
| E5 Disabled text ratio recorded | info | Exempt, still reported |
| E6 Transient states (hover) recorded, not failed | info | Cursor is a second cue |
| E7 A `_docs/Contrast Result` per pair × mode | warning | Passes are evidence |

A pass in Light and a fail in Dark is a **fail**.

When E2 fails, prefer adding a second cue that passes — a ring, a weight change — over
deepening the failing one until it collides with a neighbouring state.

---

## F · States

| Check | Sev | Detail |
|---|---|---|
| F1 `default`, `hover`, `active`, `disabled` rendered | blocker | |
| F2 `focus-visible` rendered | blocker | Most-missed, most-broken |
| F3 Forced variants, not detached snapshots | warning | Snapshots go stale invisibly |
| F4 Matrix covers states × modes | warning | |
| F5 Disabled uses more than opacity | info | Opacity alone often fails contrast |
| F6 Loading defines what happens to the label | warning | |
| F7 **Orthogonal states are separate properties** | blocker | If two states co-occur in reality they cannot be values of one variant. Test by name: `unread`+`selected`, `selected`+`disabled`, `focus-visible`+`hover`, `read-only`+any interaction state. A tab set opens with one tab selected *and* carrying an unread dot — a single `state` enum cannot express it |
| F8 Visual precedence documented where states collapse | warning | If `selected` supersedes `unread` visually, say so — both stay true in data |

---

## G · Accessibility

| Check | Sev | Detail |
|---|---|---|
| G1 Spec block present and valid YAML | blocker | |
| G2 `role` maps to a real ARIA APG pattern | blocker | Link it |
| G3 Keyboard table non-empty for interactive components | blocker | |
| G4 Keyboard matches the APG pattern | warning | Names divergence |
| G5 Accessible-name strategy stated | blocker | |
| G6 Focus model documented | warning | Roving tabindex vs. per-element |
| G7 Target size ≥ 24×24 | warning | [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum); exactly 24 = no tolerance |
| G8 Section 09 matches the spec block | blocker | Two sources disagreeing |
| G9 Custom events declared | warning | Feeds the React wrapper |

---

## H · Content

| H1 Labelling rules | warning | |
| H2 Long-string example rendered | warning | ~2× expected |
| H3 RTL example rendered | warning | Include whether key semantics mirror |
| H4 Truncation behaviour | warning | |
| H5 Locale-derived content marked as such | warning | Anything from `Intl` must not be hardcoded, and values that look like duplicates or typos in another locale must be marked correct so nobody "fixes" them |

---

## I · Lifecycle

| I0 **`owner` matches the Figma account handle** | warning | From `whoami`, not hardcoded and not derived from an email. Changelog attributions use the same string |
| I1 Status badge present | warning | |
| I2 `ready-for-dev` only with zero blockers | blocker | The gate |
| I3 Storybook URL resolves | warning | |
| I4 Docs URL resolves | warning | |
| I5 Code Connect mapped | info | |
| I6 Changelog entry for the current version | warning | |

---

## J · Text layout — run over the handoff frame AND the kit page

Full recipes, sweep script and heuristic tuning in
[text-layout.md](text-layout.md).

| Check | Sev | Detail |
|---|---|---|
| J1 No `textAutoResize` of `NONE` or `TRUNCATE` | blocker | A fixed box that clips silently |
| J2 No `FILL` + `WIDTH_AND_HEIGHT` | blocker | Hug fights fill; hug wins and the box collapses |
| J3 Every `FILL` text has a `FIXED`-width ancestor | blocker | Otherwise `FILL` resolves to content width and short strings wrap per character |
| J4 No container hugging horizontally while holding a `FILL` child | blocker | Neither side has a width to give |
| J5 No short string wrapping | blocker | `height > lineHeight × 1.6` with `< 24` characters is a starved box |
| J6 No multi-character text under 8px wide | blocker | A single glyph may legitimately be narrow; two cannot |
| J7 No text overflowing a clipping ancestor | blocker | Compare against parent inner height, not the frame |
| J8 Column layers are `FIXED` width | warning | A hugging label destroys row alignment |

**Heuristic tuning is part of the check.** The first version of this sweep flagged close to
half the nodes in a frame, of which a handful were real. An over-eager sweep trains people to ignore it. Fixed-height
cells, single glyphs, and type styles with `lineHeight ≤ fontSize` are all legitimate —
test against the style's line-height and the parent's inner height, not against font size.

---

## K · Parts

Full decision table in [sub-components.md](sub-components.md).

| Check | Sev | Detail |
|---|---|---|
| K1 Every stateful / repeated part is a component | blocker | ≥2 states, ≥3 repeats, or independently focusable. Otherwise its state is baked into parent layers |
| K2 Part is classified public or internal | warning | Naming encodes it; getting it wrong makes the later fix breaking |
| K3 Internal part lives in the parent's `01 · Component` | warning | Not loose on the canvas |
| K4 Internal part tokens are namespaced under the parent | warning | `tabs/tab/*`, not `tabs-tab/*` |
| K5 Public part has its own handoff frame | warning | And the parent references it by node id rather than restating it |
| K6 No duplicate part | warning | Search by name **and** structure before creating |
| K7 Nesting depth ≤ 1 | warning | A part of a part usually means the parent should be split, or the middle layer promoted to public |
| K8 **Parent has zero part blockers** | blocker | Rollup. Attributed: `blocker · part "Tab" · F7` |
| K9 `08 · Spec` records each part and its visibility | warning | So the code side knows whether to emit an export or a private class |

---

## L · Visual

Rules and rationale in [visual-design.md](visual-design.md).

| Check | Sev | Detail |
|---|---|---|
| L1 Sections are grouped into chapters | warning | Contiguous by number. Uniform spacing asserts everything is equally related |
| L2 Spacing scale applied | warning | 96 chapter · 48 section · 20 header→content · 12 rows. The ratio matters more than the numbers |
| L3 Content blocks are carded, headers are not | warning | Section headers stay on the page so they read as labels for the block below |
| L4 **No card shares the page's surface token** | blocker | Same token = invisible card. Fails silently; re-check after any surface change |
| L5 Chapter header is a different treatment, not a bigger title | warning | 2px rule + uppercase eyebrow vs. a 20px section title |
| L6 Prose constrained to ~760px | warning | 1152px at 14px is ~160 characters. Tables and matrices stay full width |
| L7 Card treatment not applied to chips | warning | Keycaps and badges are chips; gate on width (~400px) |
| L8 Post-visual sweeps clean | blocker | Text layout, unbound chrome paints, and instance integrity re-run after grouping — reparenting touches every node |
| L9 **Content bindings survived the styling pass** | blocker | Every paint inside the documented component and its part sets is still variable-bound. Count before and after; a drop means the pass reached into content |
| L10 Chrome styling matches what was chosen | warning | Generic by default; file tokens only if the user asked. Mode panels and token swatches are file tokens either way |
| L12 **Sheet reads against the Figma canvas** | warning | White fill, radius, hairline border and a soft shadow. A grey page surface disappears into the canvas |
| L13 Type scale applied | warning | display 44 · title 28 · subhead 20 · body 14. A section title at 20 reads as emphasis, not hierarchy |
| L14 Not every block is a card | warning | Thin sections paired side by side; prose uncarded; tint without border |
| L15 **Anatomy pins sit in a gutter with leader lines** | warning | Placement rule for the pins `A13` requires. On the artwork they cover what they annotate and collide where parts nest |
| L11 Kit page is laid out, nothing loose | warning | Cover with palette and type scale, components grouped in labelled cards, deprecated demoted |

---

## Readiness score

A single number people can track, weighted by category pass rate:

| Category | Weight |
|---|---|
| Tokens (C) | 20 |
| Contrast (E) | 20 |
| Accessibility (G) | 15 |
| States (F) | 15 |
| Modes (D) | 10 |
| Structure (A) | 10 |
| Contract (B) | 10 |

```
score = Σ ( weight × passRate(category) )
```

**Always render the score with the blocker count, never alone.** A component with one
blocker and forty passes scores in the nineties and is not shippable. The score is a trend
line; `ready-for-dev` is gated on blockers being zero and nothing else.

---

## Machine-readable output

Emit alongside the prose report, so CI can gate on it and the next run can diff it:

```json
{
  "component": "Tabs",
  "node": "48:210",
  "mode": "RE-AUDIT",
  "at": "2026-08-18",
  "score": 84,
  "counts": { "blockers": 0, "warnings": 2, "info": 1 },
  "readyForDev": false,
  "findings": [
    { "id": "C13", "severity": "warning", "priority": "next",
      "node": "502:8", "detail": "token name does not match its binding" }
  ],
  "delta": { "fixed": ["E2", "F7"], "new": ["C13"], "since": "2026-08-17" }
}
```

`delta` compares against `lastRun.findings` in the kit config block, keyed on `id + node`.

---

## Report format

```
figma-specsheet · Tabs · RE-AUDIT (dry run)

  handoff frame   72:1180     sections   13 of 13
  component       48:210       tokens     14 bound · 0 hardcoded
  modes           Light ✓ Dark ✓  contrast  22 checks · 18 pass · 2 fail · 2 exempt

  CHANGED SINCE v1.1.0 (2)
    tab        hardcoded 32px height, radius 6  →  size/32 + radius/6
    unread     value of `state`                 →  boolean + dot

  BLOCKERS (2)
    E2   unread tint vs surface · Light 2.1:1 · Dark 2.4:1 · needs 3:1
    F7   unread is a value of `state` — cannot co-occur with selected

  WARNINGS (2)
    C13  tabs/tab/unread-hover bound to a fill, named as a hover token
    B8   unread-dot present in 18 of 20 variants — vestigial

  INFO (1)
    C6b  tabs/tab/background/unread → color/blue/500/30 · primitive-justified

  FIX PLAN            risk → what I may do        priority → what to do first
    additive     1 — RTL example                          [safe]      · eventually
    corrective   2 — rename token, remove vestigial nodes [diff]      · next
    breaking     1 — split `state` into state + unread    [approval]  · first

  SINCE 2026-08-17     fixed E2, F7 · new C13

  needsHumanReview: 2 blockers — do not run read-figma-component.

  ── Some of these may be deliberate. C13 and B8 in particular can be
     intentional in a system that has made a different call. Reply with a
     check ID to downgrade it for this component and I will record it in
     the kit config, so it stops being raised on every run.
```

**Two axes on the fix plan.** *Risk* (`additive` / `corrective` / `breaking`) governs what
the skill may do without asking. *Priority* (`first` / `next` / `eventually`) is what the
human should do Monday. They are different questions and they disagree often — a breaking
fix is frequently the most urgent one.

**The closing note is not politeness.** A rubric that presents itself as infallible gets
ignored wholesale the first time it is wrong about a deliberate decision. Inviting the
downgrade — and *recording* it in the config block — is what keeps the audit trusted on the
tenth run instead of muted after the second.

---

## Batch mode

`Audit all figma components` returns a scorecard:

```
COMPONENT   SECTIONS  TOKENS     MODES  CONTRAST  BLOCKERS  STATUS
Button      13/13     18 ✓       ✓✓     12/12     0         ready-for-dev
Tabs    13/13     10 ✓       ✓✓     18/20     2         in-review
Badge        9/11      6 ✓       ✓✗      4/4      1         draft
```

Fan out one `use_figma` call per page, issued in parallel in a single message. Never loop
`setCurrentPageAsync` inside one script.
