# figma-specsheet — Changelog

## v3.2.1 — 2026-08-21

No rule changes. Everything here removes information about the file the skill was developed
against.

| # | Change | Reason |
|---|---|---|
| 98 | **Every measurement taken from a real file replaced with a generic statement** — contrast ratios, variant and instance counts, node and text-node totals, pixel spreads, opacity values | A rule earns its place by explaining the failure it prevents, not by publishing the numbers that exposed it. "The width heuristic flagged dozens of correctly-designed label columns" carries the whole argument; the exact count only tells a reader about someone else's file. Worked examples keep obviously-synthetic values |
| 99 | **The scrub denylist replaced with a general rule.** `check.py` no longer carries a list of specific terms; it rejects any real `@handle` in a worked example, matching rubric `I0` | The denylist was two bugs at once. It listed a **common component name**, so a contributor documenting a component of that name would have been rejected by a rule encoding one private repo's history as universal. And a denylist is a public list of exactly what was scrubbed, which is the opposite of scrubbing it |
| 100 | **Example owners and identities are fictional throughout** | An example owner is illustration, not attribution. Authorship belongs in `LICENSE` and the README, and stays there |

**The standing rule, now in CONTRIBUTING.** A worked example may describe a failure in as
much detail as it takes to be convincing, and may not carry a measurement of a real file.
Those are compatible: the mechanism is what teaches, and the number is what leaks.


## v3.2.0 — 2026-08-21

Everything here came from running the skill end-to-end against a large multi-axis component
— the first full CREATE since v3.0. Fourteen defects, every one found by something going
wrong rather than by review.

| # | Change | Reason |
|---|---|---|
| 81 | **The section-discovery contract now constrains type and parent.** `SKILL.md`, `frame-template.md`, `visual-design.md` and `read-figma-component` all updated together; new pitfall §19 | Figma auto-names a TEXT node after its own content, so a sizes table rendering a padding pair produced a node matching `/^\d\d · /`. The sweep reported **more sections than the frame has**. Anything parsing sections by name would have read padding values as sections, silently. This was the single most dangerous defect in the skill |
| 82 | **Post-write verification must assert the intended value**, not merely a self-consistent result | A reflow of an entire variant set was ignored by an auto-layout `WRAP` parent, and the verification **passed** — no overlaps, all in bounds, both true of a wrapped flow. Only a screenshot caught it. A check that can pass on a result you did not ask for is a sanity check, not a verification |
| 83 | **New pitfall §18** — auto-layout ignores `x`/`y`, and component sets are frequently `WRAP` | Nothing throws. `layoutPositioning` stays `AUTO` and Figma places by child order |
| 84 | **New pitfall §17** — `description` HTML-escapes quotes | `"¿Eliminar?"` stores `&quot;¿Eliminar?&quot;`. It is the only durable metadata channel and `read-figma-component` parses it, so the entity reaches generated code. A strict comparison also reports a failure that did not happen |
| 85 | **New pitfall §20** — `ComponentNode.instances` only sees loaded pages | The same set reported three different totals across one session, each larger than the last, with no edits. Every instance count is a **lower bound** and must say so — a user approving a breaking change is being shown the blast radius |
| 86 | **Sizing modes must be re-asserted after `resize()`** (§3 extended, corollary in post-write-verification) | A root frame created `FIXED` was later found `HUG`, silently growing to fit its widest child |
| 87 | **Content width is a constant, fixed before the first section**, and the oversized-subject rule now counts *both* paddings | Every table is laid out against the content column; step 12 changes root padding, so a moving column overflows all of them. The first attempt at the subject rule omitted the hero's padding and clipped the master |
| 88 | **`03 · Modes` gets a sufficiency rule and a stacking fallback** | The template said "the same content" without saying what content is enough, which allowed a four-button panel to claim it proved every variable resolves in both modes. Two dense panels also cannot always share one content column |
| 89 | **`04 · Variants` gets a matrix model for >2 axes**, with absent combinations stated rather than omitted | "One row per variant" means well over a hundred rows on a real component. And an omitted pairing is indistinguishable from an undocumented one — a developer will call `setProperties` toward a variant that does not exist |
| 90 | **The anatomy gutter axis is chosen from the part spread** | A left gutter assumes vertically-stacked parts. An inline control's parts spread horizontally with **effectively no vertical spread**, so every pin lands on one `y` and the collision rule pushes two off their targets — the exact failure the gutter was introduced to prevent |
| 91 | **The text sweep keys on characters-per-line, not raw width** | The width heuristic flagged dozens of correctly-designed fixed-width label columns. With the corrected one: zero issues |
| 92 | **Alpha compositing lives in one shared helper** (`E0` rewritten) | It was written correctly, then retyped minutes later in a solver with the alpha dropped, producing a wrong verdict. The rule that exists to prevent this error was broken by re-typing it |
| 93 | **Focus indicators are measured against adjacent layers** (`E3`/`E4` rewritten) | Measuring an inner ring against a canvas it never touches gives a very different number from measuring it against the halo it does touch. `E4` now requires identifying every layer of the indicator first — a halo matching the canvas is a gap, not a second ring |
| 94 | **The config block is found by name and merged, never replaced** | A truncated scan of the kit cover missed an existing `config` node and reported "no config block"; the write-back then overwrote it. `severityOverrides` are user decisions and were destroyed silently |
| 95 | **`C18` extended to `opacity`; new `A14` and `A15`; four verdicts instead of two** | A disabled variant dimmed by an unbound opacity looks tokenised because every fill beside it is bound. And `exempt` is not `pass` — WCAG 1.4.3 excludes inactive components, so reporting a failing disabled pair either way is wrong |
| 96 | **`_docs/Contrast Result` needs `exempt` and `info` variants** | The rubric depends on both; the kit offers only `pass \| fail`, so exempt rows were rendered as passes with the exemption buried in a column |
| 97 | **`scripts/check.py` guards the discovery contract** | The defect in 81 is a one-character regression away from returning |

**What held up.** The `F7` gate stopped the run before writing anything, unprompted, and
prevented documenting a state model that would have had to be rebuilt. Atomic rollback
worked six times — every failed verification left the file clean. And verification caught
three real defects that review had missed.

**What that says about the shape of the skill.** Every defect above was found by *use*, not
by reading. Nine of the fourteen were silent — no error, no thrown exception, a result that
looked correct. That is the failure mode this skill exists to catch in other people's files,
and it is the failure mode it kept producing in its own output.


## v3.1.0 — 2026-08-20

Packaged for public release. No behavioural change to the skill itself — the rules, the
rubric and the write path are identical to v3.0.1.

| # | Change | Reason |
|---|---|---|
| 74 | **Renamed `document-figma-component` → `figma-specsheet`.** Frontmatter `name`, the pipeline diagram, the report headers and the changelog title all updated | The old name described the mechanism; the new one describes the artifact. Sibling skills (`sync-figma-tokens`, `read-figma-component`, `build-figma-component`) keep their names — the pipeline references in `SKILL.md` are unchanged and still resolve |
| 75 | **Repo scaffolding** — `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`, `.gitignore`, issue and PR templates, and `scripts/package.sh` to build the `.skill` archive | The skill is portable across projects; it needed to be installable by someone who did not build it |
| 79 | **Three rules that contradicted each other resolved in favour of the later decision.** `A13` no longer requires pins *on the artwork* — it requires every legend entry to have an anchored pin, and `L15` owns where the pin sits (gutter, leader line). The type scale is 44 / 28 / 20 / 14 everywhere; `docs-kit` and `frame-template` still carried the retired 28 / 20. The root frame is the white sheet; `frame-template` still said "semantic surface token" and `visual-design`'s own common-region block still described the pre-sheet page/card model | These were not style preferences in tension — `A13` was a **blocker** and `L15` a **warning** demanding the opposite thing, so no frame could satisfy the rubric. Changes 61 and 63 made the newer call and never swept the files that stated the old one. Entries 18, 29 and 47 below are superseded |
| 80 | **Counts in the README corrected against the files** — 119 checks not 46, a 14-step CREATE flow not 12, 15 non-negotiables not 14 | 46 predates sections J, K and L entirely. A number in a README is a claim, and this one had been wrong for three releases |
| 77 | **Every worked example re-cast onto a neutral `Tabs` / `Tab` pair**, and the pilot component's audit report removed from the repo | The examples came from a real client file — its component name, its node IDs, its token values. A reader would reasonably conclude the skill was written for that one component, and the file's node IDs are not ours to publish. `Tabs` has the same structural shape (a parent owning an internal, repeating, independently-focusable part, with a boolean that co-occurs with `selected`), so every lesson survives the swap |
| 78 | **`scripts/check.py` fails on identifiers from a real file** — a live Figma file key, or a real owner handle in a worked example | A neutralisation that is not enforced quietly reverts the first time someone pastes a real audit into a reference file |
| 76 | **CI link check** on every push and PR (`.github/workflows/lint.yml`) | Progressive disclosure only works if the links between `SKILL.md` and `references/` resolve. A dead reference link means a rule silently stops being loaded — the failure mode is a skill that quietly gets dumber, which nothing else would catch |

**On the examples.** The reference files teach through worked examples, and those examples
were the pilot component throughout — which made the skill read as if it only knew how to
document that one thing. They are now a neutral `Tabs` / `Tab` pair. The changelog below is
the exception: it is a historical record, so the pilot is referred to but never renamed,
because renaming it would be a fabrication rather than a neutralisation.

**On the rename.** The old name described the mechanism — it told you what the skill did
*to* something. The new one names the artifact you get, and "spec sheet" resolves to the
same picture for a designer and for an engineer, which is the whole test a skill name has
to pass in a list of thirty others. It also scans as a command: `/figma-specsheet Tabs`.

Anything that reads a skill by name — a project that pins it, a prompt that invokes it by
slug — breaks on upgrade. That is the entire cost, and it is paid once. The trigger phrases
in `SKILL.md` (`Document figma component {Name}`, `Audit figma component {Name}`) are
unchanged, so natural-language invocation is unaffected.

**The frame node name is deliberately *not* renamed.** The artifact on canvas stays
`DS · {Name} · Handoff`, because `read-figma-component` finds it with
`page.findOne(n => n.name === \`DS · ${Name} · Handoff\`)`. Renaming the node would silently
break every downstream read for zero benefit — the skill is the specsheet builder, the node
is the handoff frame, and only one of those two names is a contract.


## v3.0 — 2026-08-19

Adopted from a survey of four published Figma skills. Six of eleven candidate patterns taken,
three already covered, two probably unbuildable here.

| # | Change | Source |
|---|---|---|
| 65 | **New `references/post-write-verification.md`.** Every write script verifies its own returned node IDs and **throws** on failure. Scripts are atomic, so a failed assertion costs nothing and leaves the file clean | claude2figma |
| 66 | **Symptom indexes** on `figma-api-pitfalls`, `text-layout` and `audit-rubric`. You arrive holding an error string, not a section number | ui-ux-pro-max, scaled down |
| 67 | **Source axis on token resolution** — published library variable before local. Binding a local duplicate silently detaches the node from the library. New `C16`, and `C17` for a local that shadows a published one | claude2figma |
| 68 | **Config block on the kit cover.** Chrome mode, locale, severity overrides and `lastRun` in YAML. Stops the questions repeating, makes overrides permanent, and turns repeat runs into a delta | design-system-ops |
| 69 | **Graceful degradation at preflight step 0.** An unreachable file offers a partial audit or a queued plan. Hard stops stay for *design* preconditions — those make the output wrong, not late | design-system-ops |
| 70 | **Readiness score**, weighted by category, always rendered **with** the blocker count. `ready-for-dev` stays gated on blockers alone — a score is a trend line, not a gate | work-with-design-systems |
| 71 | **JSON audit output** with a `delta` against `lastRun`, so CI can gate and the next run can diff | work-with-design-systems |
| 72 | **Priority as a second axis** on the fix plan. Risk governs what the skill may do; priority is what the human does Monday. They disagree often — a breaking fix is frequently the most urgent | design-system-ops |
| 73 | **Calibration note** closing every report, with a hook: reply with a check ID to downgrade it, recorded in the config. A rubric that presents itself as infallible gets muted the first time it is wrong about a deliberate decision | design-system-ops |

**Why 65 is the important one.** Four failures in the pilot — unbound content
paints, six black key caps, a cloned variant rendering stale text, labels wrapping per character —
all came from scripts that returned success with valid node IDs. The information to catch
each was already in scope at write time. Nothing was missing except the assertion.

The rubric's late-running equivalents (`A12`, `C15`, `L9`) stay, because a frame edited by
hand between runs still needs them. But they should now almost never fire. **If one does,
the write's assertions were incomplete — fix the assertion, not just the node.**

### v3.0.1 — `C18`, found by generating code

Checking the generated component against this file surfaced three CSS variables that
would never resolve: `--semantic-size-border-default`, `--semantic-size-border-focus` (the
system has no `size/border/*` scale) and `--typography-weight-semibold` (the variable is
`weight/Semi Bold`, so Style Dictionary emits `semi-bold`).

The first two are the interesting ones. **`C1` covers fills, sizes and radii but never
checked `strokeWeight`** — so the component's 1px border and 2px focus ring were literals
the whole time and the audit passed them. New check `C18`.

Worth noting how it was caught: not by the audit, but by generating code from the component
and checking whether the variables it referenced existed. **Emitting code is itself a test
of the token map** — a gap that an in-Figma audit can miss shows up immediately as a
variable that resolves to nothing.

### Spike resolved: comments are not reachable

Searched the Figma MCP surface for any comment capability. There is none — the tool set
covers assets, Code Connect, design context, metadata, screenshots, variables, video export
and `use_figma`, and nothing else. Combined with the Plugin API having no comment access,
**the comment-thread task queue cannot be built in this environment.** Closing it rather
than leaving it open; revisit only if a REST-backed comment tool appears.

### First v3.0 run

```
score 100 · blockers 0 · warnings 0 · 46 of 119 checks applicable
content paints all bound · 0 unbound

(Per-category tallies from this run were recorded against the pre-J/K/L rubric
and no longer map onto the current section letters, so they are not reproduced.)
```

`C16` (library-before-local) is recorded as **not applicable**, not as a pass: this file has
no subscribed library collections, so the preference is unverifiable. Counting an unverifiable
check as a pass is how a score starts lying — the config block now carries a `notApplicable`
list for exactly this reason.

The config block is live on the kit cover and holds `lastRun`, so the next run reports a
delta instead of a fresh wall of findings.

### Considered and not taken

- **Full BM25 search over data files.** Over-engineering at 13 files with on-demand loading. The symptom index gets most of the value.
- **Finding IDs separate from check IDs.** Ours are check IDs, stable across runs and components. `check-id + node-id` gives trend comparison without a second scheme.
- **Three-layer token indirection for `tokens.css`.** That is `build-figma-component`'s concern; this skill writes to Figma only.
- **Comment threads as a task queue.** The most original idea surveyed, and likely unbuildable: the Plugin API has no comment API, and `use_figma` runs in the plugin sandbox. Needs a REST spike before committing.
- **Shared `_shared/` references across the four pipeline skills.** Correct, and deferred — it means touching `sync-`, `read-` and `build-` at the same time.

## v2.8 — 2026-08-18

Visual critique round: blocky, background lost against the canvas, titles small, pins odd.

| # | Change |
|---|---|
| 59 | **The frame is a sheet, not a panel.** Figma's canvas is mid-grey, so a grey page surface disappears into it. White fill, 28 radius, hairline border, soft shadow — and inner blocks tint *downward* from the sheet. `L12` |
| 60 | **Borderless tinted blocks.** Border + tint + radius is three separations doing one job, and the result is a stack of slabs. The tint alone separates |
| 61 | **Type scale up a step** — display 44, title 28, subhead 20, chapter 13/+10%. At 20 the section title was 1.4× body and read as emphasis, not hierarchy. Documents get viewed zoomed out |
| 62 | **Not every block is a card.** Thin sections pair side by side; prose stays uncarded; card only what is scanned. `L14` |
| 63 | **Anatomy pins move to a left gutter with leader lines.** On the artwork they cover what they annotate and collide where parts nest. Sort anchors by y before placing so leaders never cross; anchor containers at their bottom edge. `L15` |
| 64 | **`pitfalls §16`** — reading a node after `remove()` throws, including one statement later in the same loop iteration. Spreading the children array protects the iteration, not the node |

**On 59:** this inverts the usual figure/ground move. Normally the page recedes and cards
lift; here the competing surface is the Figma canvas, so the sheet has to be the bright
thing. Worth stating explicitly because the earlier version was "correct" by the general
rule and wrong in context.

## v2.7 — 2026-08-18

Chrome colour goes generic, and a bug that only surfaced because two earlier decisions met.

| # | Change |
|---|---|
| 53 | **Generic chrome palette**, verified — two text tiers (a third lands under 4.5:1 on white unless it is indistinguishable from `muted`), five tones, all fg-on-bg ≥ 5.2:1 |
| 54 | **Chrome styling is a preflight question**, defaulting to generic. Binding chrome to file tokens works in one file and moves when the product rethemes |
| 55 | **The exemption list is explicit**: documented component, part sets, mode panels, token swatches. Those keep file tokens under either answer |
| 56 | **`pitfalls §15`** — v2.5 moved parts *into* the doc frame; v2.6 recoloured everything *in* the doc frame. A name/type heuristic missed the part set, because a set's variants are `COMPONENT`, not `INSTANCE` |
| 57 | **`L9` content-binding check.** Count bound paints inside the component before and after a styling pass; a drop means it reached into content |
| 58 | **The kit page is laid out** — cover with palette and type scale, three groups in labelled cards, deprecated demoted. Nothing loose. `L11` |

**Why 56 is the one to remember.** It unbound the label fill on every variant in the
part set and every instance inheriting from them, and *nothing looked wrong* — the
literal happened to match the light-mode value. It would have failed in dark mode only.
Build the exempt set by **node identity** before styling, never by walking up matching
names and types: names change, and the same logical thing is a set, a variant, or an
instance depending on where you caught it.

## v2.6 — 2026-08-18

Visual design. The frame was correct and unreadable — 13 sections, uniform gaps, one flat
surface, 9,900px tall with no landmarks.

| # | Change |
|---|---|
| 44 | **New `references/visual-design.md`** — gestalt rules applied: proximity, common region, figure/ground, similarity, measure |
| 45 | **Chapters.** 13 sections grouped into 5, contiguous by number so reading order and the numbering contract both survive. New `_docs/Group Header` |
| 46 | **Spacing scale** — 96 chapter · 48 section · 20 header→content · 12 rows. The ratio (~2× per level) matters more than the values |
| 47 | **Common region.** Page recedes to `surface/sunken`; content blocks are cards on `surface/popover`. Section headers stay *outside* the card so they read as labels for it |
| 48 | **Measure.** Prose pinned to 760px — 1152px at 14px is ~160 characters. Tables stay full width; they are scanned, not read |
| 49 | **A chapter header is not a bigger section header.** Different treatment (2px rule + uppercase eyebrow), or it reads as the same level slightly louder |
| 50 | **New rubric section `L`** — L1–L8, including `L4`: no card may share the page's surface token |
| 51 | **Discovery contract updated** — sections are nested in groups now, so `root.children` no longer finds them |
| 52 | **`pitfalls §14`** — variable bindings set on **instance children** store the binding and render the literal. Six keycaps went black while every check reported success |

**Two things worth carrying forward.** Figure/ground fails silently: moving the page to
`surface/sunken` made four inner blocks using the same token vanish, with no error and a
perfect structure. And visual work must come **last** — regrouping reparents every section,
so the text sweep, the unbound-paint sweep and the instance check all have to run again
afterwards.

## v2.5 — 2026-08-18

Sub-components. The skill had no guidance at all, and the pilot paid for it:
the parent was documented, then `Tab` was restructured, then sections `01`, `06`
and `07` all had to be rebuilt.

| # | Change |
|---|---|
| 37 | **New `references/sub-components.md`** — when to extract, public vs internal, where parts live, how they're documented, reuse, depth, rollup |
| 38 | **Part discovery is a CREATE gate**, at step 2 — before property normalisation, before tokens. Every parent section is a description of its parts, so resolving them late means rebuilding those sections |
| 39 | **Public vs internal is the decision that drives everything**, and naming encodes it — `badge/*` vs `tabs/tab/*`. Promotion is therefore breaking, and never silent |
| 40 | **Internal parts live in the parent's `01 · Component`**, not loose on the canvas — same rule as the parent master |
| 41 | **New rubric section `K`** — K1–K9, including `K8` rollup: a parent is never `ready-for-dev` while a part has blockers |
| 42 | **`parts[]` added to the spec block** with a `public` flag, so `build-figma-component` knows whether to emit a package export or a private class |
| 43a | **`owner` comes from the Figma account.** `figma.currentUser` is not a supported API here, so identity is resolved via MCP `whoami` and passed into the script as a literal. Never hardcoded, never derived from an email local part or git author. Blank-and-flagged if unresolvable. `I0`, `pitfalls §13` |
| 43 | **Mid-build discovery has a procedure**: stop, report which sections it invalidates, fix the part, re-run those sections. Finishing first and patching after costs more, every time |

**The rule in one line:** resolve parts before documenting the parent, because the property
table, the state matrix and the token table are all descriptions of the parts.

## v2.4 — 2026-08-18

Docs chrome no longer depends on the host file's text styles.

| # | Change |
|---|---|
| 33 | **Chrome type is self-contained.** A generic sans + mono resolved by availability probe, applied directly to nodes. The kit previously resolved `S['Heading/Card']` — a name that exists in exactly one file. `A16` |
| 34 | **An 11-role type scale** — display, title, subhead, eyebrow, bodyLg, body, bodyStrong, label, badge, mono, monoSm — documented with sizes, weights, line-heights and tracking |
| 35 | **The chrome/content boundary.** The restyle sweep must skip the documented component and its instances. On a full frame that is the large majority of text nodes. `A17` |
| 36 | **Colour has the same problem, flagged not fixed.** Chrome colour still resolves Semantic tokens by exact name. The resolver-with-fallback pattern is documented; it is not implemented |

**The reasoning:** documentation chrome is infrastructure, not product UI. Coupling it to
the file's type styles means it works in one file and silently degrades in the next, and
that a product type change reflows every doc frame. The component being documented is the
opposite — it must render in the file's real styles and tokens, or the documentation is
lying about what it looks like.

## v2.3 — 2026-08-18

Three gaps found by reading the built frame rather than the build logs.

| # | Change |
|---|---|
| 29 | **Anatomy pins must sit on the artwork.** v2.2 built a numbered legend and placed *zero* pins on the component — the numbers referenced nothing. Pins are now anchored to real nodes by computed geometry, with a different corner per part (nested parts share corners) and a collision nudge. `A13` |
| 30 | **Properties render as a table.** New `_docs/Property Row` with `kind = header \| body` sharing one column grid. A prose list has no alignment and drifts the moment a value changes length. `A14` |
| 31 | **Spec block is monospace.** Indented structured data in a proportional font is unreadable. Use an existing mono style, else apply a generic mono family directly — **never create a text style**, that is a type-system decision. Detach from the proportional style first or it fights the override. `A15` |
| 32 | **Creation order** added to `text-layout.md`. `resize()` after setting sizing modes pins the frame at the resize height — and the natural way to write component-creation code does exactly that. Every row of the new property table collapsed to 10px on the first build |

**Worth noting about 32:** this is the same rule already documented in `pitfalls §3`, and I
still hit it, because the fix guidance was written for *repairing* a node and the bug
happens at *creation*. Rules stated in the wrong tense don't fire. The helper is now
written out in full so there is nothing to re-derive.

## v2.2 — 2026-08-18

Text containers. Reported as "very common with Claude editing or creating in Figma", and
confirmed: the handoff frame had `value` layers rendering `v2` as `v` over `2` and `1.2.0`
down five lines.

| # | Change |
|---|---|
| 23 | **New `references/text-layout.md`** — the four valid sizing recipes, the container trap, the sweep script, and heuristic tuning |
| 24 | **`FILL` is a promise deferred upward.** A `FILL` text node has no width of its own; it inherits whatever the ancestor chain pins. If every ancestor hugs, it resolves to *content* width and short strings wrap per character. Verify the fixed-width ancestor, never assume it |
| 25 | **The container trap.** A container hugging horizontally while holding a `FILL` child is always a bug — neither side has a width to give. Now a searchable shape and a blocker (`J4`) |
| 26 | **The sweep is a mandatory build step**, over the handoff frame *and* the kit page. Both must return zero |
| 27 | **New rubric section `J`** — eight checks, J1–J8 |
| 28 | **Heuristic tuning is part of the check.** The first sweep flagged close to half the nodes; a handful were real. Fixed-height cells, single glyphs, and type styles with `lineHeight ≤ fontSize` are legitimate. An over-eager sweep is worse than none |

**Why this class of bug survives every other check:** the script reports success, the
structure is correct, the tokens are bound, and the property values are right. Only the
rendered geometry is wrong — which is the same lesson as `A12`, one level deeper. The
audit has to measure the canvas.

## v2.1 — 2026-08-18

From re-running v2 against the pilot component and fixing what the run exposed.

| # | Change |
|---|---|
| 16 | **The component master lives in `01 · Component`.** The handoff frame is the component's home — one place to find the thing and its spec, and no way for them to drift. Superseded standalone doc frames are deprecated, not deleted. `frame-template` |
| 17 | **Section Header instances must be set to `FILL`.** The kit main's width is its own canvas size; a `FIXED` instance stops its rule short of the section edge — in all 13 sections at once. `A11` |
| 18 | **Type scale stated.** Component name 28, section title 20, number 12, body 14–16. The component name is the document title, not a section heading |
| 19 | **`clone()` drops `componentPropertyReferences`.** Nothing throws, `setProperties` reports success, and the canvas renders stale text. `pitfalls §11`, `A12` |
| 20 | **Switching a variant drops non-variant overrides.** Set variant first, then everything else — the same ordering rule as re-pointing an orphan. `pitfalls §12` |
| 21 | **Column layers are FIXED width with `textAutoResize: HEIGHT`.** A hugging label collapses and destroys row alignment. Only the last column uses `FILL` |
| 22 | **`primitive-justified` renders neutral, not amber.** Flagging a justified primitive as debt trains people to ignore the column |

**A12 is the check worth having.** `componentProperties` reports intent; `node.characters`
reports reality. When a property reference is broken the two disagree and only the canvas
is telling the truth — so the audit reads the canvas.

## v2 — 2026-08-18

Everything here came from piloting v1 end-to-end in a production file, including
a second pass after the designer edited the component underneath the documentation.

### Corrections — v1 was wrong

| # | Was | Now |
|---|---|---|
| 1 | Ownership via `setSharedPluginData` | **Unavailable in `use_figma`.** And `description` does not exist on FRAME nodes. Discovery is by name; `ref`/`kit` live in visible Meta Rows. `pitfalls §1`, `SKILL → Discovery contract` |
| 2 | Contrast on raw RGB | **Alpha composited against the real backdrop first.** Raw RGB reported a ratio in the teens where the true value was under 2:1 — an invisible focus ring passing the audit. `token-rules → Contrast gates`, `rubric E0` |
| 3 | "Typography binds text styles, only text styles" | Two valid strategies; variables are correct when one axis varies by state. Never mix **on one node**. `SKILL rule 6` |
| 4 | `semantic-gap` for every Primitive alias | Split into `semantic-gap` (warning) and `primitive-justified` (info, requires a written reason). Alpha tints have no purpose-level meaning worth naming. `token-rules` |
| 5 | Component collection must be single-mode | **Match the file.** Multi-mode is fine; the aliasing strategy depends on whether frames pin Semantic and Component together. Verify before choosing. `SKILL rule 4`, `rubric D5` |
| 6 | Do Card + Dont Card as two components | One `_docs/Guidance Card` with `kind = do \| dont` |

### Additions — v1 was incomplete

| # | Addition |
|---|---|
| 7 | **Preflight inventories FLOAT and STRING variables**, not just COLOR. v1 hardcoded `32` and `radius 6` while `size/32` and `radius/full` already existed |
| 8 | **F7 — orthogonal states.** If two states co-occur in reality they cannot be values of one variant. A tab can be selected *and* unread at the same time |
| 9 | **RE-AUDIT mode.** The component changing underneath the docs is the common case. Leads with a change table; `07 · Tokens` is the baseline |
| 10 | **C13** — token name must match the property it is bound to. **C14** — descriptions must not describe a treatment two revisions old |
| 11 | **A9** — deleting a variant silently orphans its instances; they keep rendering and fail `setProperties` |
| 12 | **C15** — a stale name→variable map yields an unbound black paint without throwing |
| 13 | **`indicator`** added to the closed property vocabulary, plus rename-on-retreatment |
| 14 | **H5** — locale-derived content marked as such, so legitimately repeated values aren't "fixed" |
| 15 | **`references/figma-api-pitfalls.md`** — new. Ten environment constraints that produce output which looks fine and is broken |

### The two that cost the most time

**Instance subtrees are immutable.** `appendChild` into an instance throws, so a kit
component with a `slot` frame can never be filled. Mode panels are plain frames; only
`INSTANCE_SWAP` works as a slot. A kit component can style a container, not be one.

**`primaryAxisSizingMode` maps to a different physical axis per `layoutMode`** — width for
`HORIZONTAL`, height for `VERTICAL`. Combined with `resize()` resetting sizing modes, this
collapsed six kit components to 10px tall while every script reported success.

### Still open

- `read-figma-component` must be updated to parse `08 · Spec`, or this skill writes data
  nothing reads.
- No mechanism exists to detect a renamed handoff frame beyond a name search. A rename
  orphans the frame.
