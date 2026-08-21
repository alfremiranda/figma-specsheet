---
name: figma-specsheet
description: Creates or audits a component's handoff documentation frame in Figma — anatomy, modes, states, tokens, accessibility, do/don't — rendered visually for designers and machine-readably for devs. Creates missing Component variables, resolving Semantic first and falling back to Primitives with a justification. Always validates light and dark. Use when the user says "document component X in Figma", "audit component X", "create the handoff frame for X", "check X for missing tokens or dark mode", or asks for a Figma component spec / handoff / redline.
---

# Skill: figma-specsheet

Builds and maintains the **handoff frame** for a design system component in Figma —
the artifact a designer reads and `read-figma-component` parses.

Three modes. The skill detects which one applies.

| Mode | Condition | Behavior |
|---|---|---|
| **CREATE** | No handoff frame found | Scaffold the full frame from template |
| **AUDIT** | Frame exists, component unchanged since | Run the rubric, report, apply only what's approved |
| **RE-AUDIT** | Frame exists, component changed since | Lead with **what changed**, then the rubric |

```
Trigger:
  Document figma component {Name}
  Document figma component {Name} https://figma.com/design/...?node-id=...
  Audit figma component {Name}          (dry run)
  Audit figma component {Name} --apply
  Audit all figma components
```

---

## Position in the pipeline

```
sync-figma-tokens          Figma variables  →  packages/tokens/source/core.json
        │
figma-specsheet            ← YOU ARE HERE. Makes the Figma side correct and complete.
        │
read-figma-component       Reads the handoff frame  →  spec JSON + story plan
        │
build-figma-component      Generates the code files
```

**Writes to Figma only.** Never touches repo files.

The payoff: because this skill writes the `08 · Spec` YAML block, `read-figma-component`
stops *inferring* roles and keyboard maps. Its `Role not determinable from Figma` flag
should never fire on a component with a valid spec block.

> `read-figma-component` must be updated to parse the spec block. Until it is, this skill
> writes data nothing reads.

---

## Load these first

`figma-use` is a hard prerequisite before any `use_figma` call. For component-set and
variable work, load `figma-generate-library` too.

| Reference | Load when |
|---|---|
| [references/post-write-verification.md](references/post-write-verification.md) | **Before any write.** How every write script proves it worked |
| [references/figma-api-pitfalls.md](references/figma-api-pitfalls.md) | **Before any write.** Environment constraints that silently corrupt output |
| [references/text-layout.md](references/text-layout.md) | **Before any write, and again after.** Text sizing recipes + the mandatory end-of-build sweep |
| [references/sub-components.md](references/sub-components.md) | **Before documenting anything with repeated or stateful parts.** Extract / public-vs-internal / rollup |
| [references/frame-template.md](references/frame-template.md) | CREATE, or auditing structure |
| [references/docs-kit.md](references/docs-kit.md) | Preflight, or the kit is missing/stale |
| [references/visual-design.md](references/visual-design.md) | **Last, after content is correct.** Grouping, spacing scale, figure/ground, measure |
| [references/token-rules.md](references/token-rules.md) | Any token resolution, creation, or mode work |
| [references/audit-rubric.md](references/audit-rubric.md) | AUDIT / RE-AUDIT |
| [references/spec-block.md](references/spec-block.md) | Writing or validating `08 · Spec` |

---

## Preflight — every run, both modes

Stop and report on failure. Never work around a failed preflight.

0. **Can the file be reached?** If the Figma connection is down or the file is
   inaccessible, do **not** hard-stop. Offer two paths:

   - **Partial audit** — from a supplied screenshot plus the spec block text. Content-level
     findings only, labelled `partial: no file access`. No token, mode or binding checks,
     because they cannot be verified.
   - **Queue the writes** — produce the full plan now and apply it when the connection
     returns.

   Hard stops stay for *design* preconditions (step 3 below): a missing `Semantic` mode
   makes the output wrong, where a missing connection only makes it late.
1. **Design file.** URL is `figma.com/design/...`. FigJam and Slides are out of scope.
2. **Collections exist.** `getLocalVariableCollectionsAsync()`. Require `Primitives`,
   `Semantic` (≥2 modes), `Typography`. Create `Component` if absent — matching the
   file's existing convention, not a default (see rule 2).
3. **Mode map resolved.** Record the Light and Dark mode IDs for every collection that
   has them. If `Semantic` has fewer than two modes, **STOP**.
4. **Inventory ALL variable types — not just COLOR.**
   `getLocalVariablesAsync()` with no filter, then group by `resolvedType`. Report the
   available scales:

   ```
   scales   size 8 · radius 8 · spacing 14 · icon 4 · typography 41
   ```

   Skipping this is how components end up with hardcoded `32` and `radius 6` while
   `size/32` and `radius/full` already exist. Assume nothing is missing until you've
   listed FLOAT and STRING variables.
5. **Docs kit present and current.** Page `_docs-kit`, components per docs-kit.md,
   version in the kit page's cover text. Build or upgrade before continuing.
6. **Text styles readable.** `getLocalTextStylesAsync()` returns > 0.
7. **Target located.** Resolve by node-id or name. More than one match → list and ask.
8. **Read the kit config block** (docs-kit.md) — chrome mode, locale, severity overrides
   and `lastRun`. Anything answered there is not asked again. `lastRun.findings` is what
   makes the run report a delta rather than a repeat.

   **Find it by name, never by scanning:**

   ```js
   const config = coverFrame.findOne(n => n.type === 'TEXT' && n.name === 'config');
   ```

   A truncated scan of the cover's text nodes will miss it and report "no config block" on a
   kit that has one — which then leads step 13 to overwrite a block it never read.
9. **Ask how the chrome should be styled** — only if the config does not already say —
   defaulting to generic:

   ```
   Chrome styling?
     1. Generic (default) — self-contained palette and type, identical in any file
     2. File design system — chrome binds this file's tokens and text styles
   ```

   Either way the documented component, its part sets, the mode panels and the token
   swatches keep the file's own tokens. Only the chrome is in question.

Emit the preflight summary before doing any work:

```
PREFLIGHT
  file          Acme DS (aBcD1234EfGh5678IjKl)
  collections   Primitives ✓  Semantic ✓ (Light, Dark)  Typography ✓  Component ✓ (light, dark)
  scales        size 8 · radius 8 · spacing 14 · typography 41
  docs-kit      v2 ✓
  target        Tabs — COMPONENT 48:210
  mode          RE-AUDIT (frame 72:1180 · component changed since v1.1.0)
```

---

## CREATE

One `use_figma` call per numbered step. Validate returned IDs before continuing.

1. **Read the component set.** `componentPropertyDefinitions` from the COMPONENT_SET
   only — never a variant.
2. **Part discovery — before any other decision.** Identify parts that need to be
   components: ≥2 visual states, repeats ≥3 times, independently focusable, or state that
   would otherwise be baked into parent layers. For each, decide **public** (own handoff
   frame) or **internal** (documented inside this one), then build and audit it clean.
   See [sub-components.md](references/sub-components.md).

   This is a gate, not a step. The property table, state matrix and token table are all
   descriptions of the parts — documenting the parent first means rebuilding them.
3. **Normalize property names** to the target HTML attributes: lowercase, kebab-case,
   values lowercase. Renaming is **breaking** — show the diff and the instance count, wait.
4. **Check the state model.** If two state values can co-occur in reality, they are
   separate properties, not values of one variant (rubric F7). Fixing this after
   documentation means redoing the documentation.
5. **Resolve tokens.** Walk the resolution order in token-rules.md. Produce a plan table.
   Write nothing yet.
6. **Show the plan and wait.** Creating variables is a library-publishing event. Show
   what will be created, what it aliases, what fell back to Primitives and why, and what
   has no match at all. No match → **STOP**, that's a design decision.
7. **Create Component variables.** Explicit `scopes` on every one. Aliases only.
8. **Bind the component set** — including size, radius and spacing, not just colour.
9. **Fix the content width, then build the frame** one section per call, per
   frame-template.md.

   `content = rootWidth − 2 × rootPadding`, and it must be settled **before the first
   section is built**, because every table below is laid out against it. Step 12 changes
   root padding; if the content column moves, every fixed-width table beneath it overflows.
   Either hold the content width constant and grow the sheet, or build tables that FILL.

   If the documented component is wider than the content column, widen the sheet:
   `width = max(1280, subject + rootPad × 2 + heroPad × 2)`. Both paddings count — omitting
   the hero's is a silent clip.
10. **Render both modes.** `03 · Modes` renders the component once per mode via
   `setExplicitVariableModeForCollection` on a **frame** (not an instance — see pitfalls).
11. **Run the text-layout sweep** over the handoff frame *and* the kit page. Both must
    return zero issues and zero risky containers. This is not optional — starved `FILL`
    text is the single most common defect in agent-built Figma, every script reports
    success while it happens, and a screenshot of one section will not reveal it.
12. **Group and style the frame** per [visual-design.md](references/visual-design.md) —
    chapters, spacing scale, cards, measure. This comes **last**: regrouping reparents
    every section, so doing it before the content settles means doing it twice.
13. **Merge the run into the kit config block** — score, blocker count, findings keyed
    on `id + node` — so the next run reports a delta.

    **Merge, never replace.** Read the block, update `lastRun` only, and preserve everything
    else. `severityOverrides` are decisions the user made during earlier runs; a wholesale
    rewrite destroys them silently and they are not recoverable except from Figma version
    history. If the block cannot be parsed, stop and report — do not overwrite it.
14. **Validate.** Run the full rubric. Re-run the text sweep, the unbound-paint sweep, and
    the **content-binding check** after the visual pass — reparenting and re-surfacing touch every node. A CREATE run
    ending with blockers is not done.

---

## AUDIT

Dry run by default. Nothing written without `--apply` or explicit approval.

1. Read the handoff frame and the component.
2. Run every check in audit-rubric.md. Do not skip ones that look fine — mode parity,
   alpha-composited contrast, and orphaned instances all fail silently.
3. Report grouped by severity.
4. Propose fixes in three buckets:
   - `additive` — missing sections, panels, rows. Safe to apply.
   - `corrective` — rebinding a hardcoded value, fixing a scope, renaming a token whose
     name no longer matches its binding. Show before/after.
   - `breaking` — renaming a component property, deleting a variant, retargeting an
     alias. **Never auto-apply.** Show the diff and the blast radius, then wait.
5. Apply only the approved set, then re-run and show the delta.

## RE-AUDIT — when the component changed underneath the docs

The common case, and the one a naive audit reports badly: it lists everything as wrong
without saying what moved.

Diff the component against the last documented state — recorded in `07 · Tokens` and
`00 · Header`, which is why those sections are load-bearing rather than decorative — and
**lead the report with a change table**:

| Area | Was | Now |
|---|---|---|
| Tab | hardcoded 32px height, radius 6 | `size/32` + `radius/6` |
| unread | value of `state` | boolean + dot |

Then the rubric. A designer's change is not a finding; only its consequences are.

---

## Discovery contract — names, because there is nothing else

> Sections are nested inside chapter groups, so they are **not** direct children of the
> root. Find them with the contract below, never by walking `root.children`.
>
> ```js
> root.findAll(n => n.type === 'FRAME'
>                 && /^\d\d · /.test(n.name)
>                 && n.parent && /^group · /.test(n.parent.name))
> ```
>
> **Type and parent are both load-bearing.** Figma auto-names TEXT nodes after their own
> content, so a table cell rendering `10 · 4` becomes a node named `10 · 4` and matches a
> bare name regex. On a real run that reported 16 sections in a 13-section frame. See
> [figma-api-pitfalls.md](references/figma-api-pitfalls.md) §19.


**`setPluginData` and `setSharedPluginData` are unavailable in `use_figma`,** and
`description` **does not exist on FRAME nodes** — only on COMPONENT and COMPONENT_SET.
There is no hidden metadata channel. Discovery is by name and by visible content.

| Thing | Contract |
|---|---|
| Handoff frame | Frame named exactly `DS · {Component} · Handoff` |
| Section | Frame named `NN · Title` |
| Component ref | `ref` row in `00 · Header`'s Meta Rows, value = node id |
| Kit version | `kit` row in the same block |
| Managed content | Anything matching the naming contract |
| Unmanaged content | Everything else — **retained**, listed as `info` |

Consequences:

- The skill may update nodes matching the contract. It may not delete or overwrite
  anything else.
- A renamed frame is orphaned. `A1` is a blocker with a "did you mean" search across
  the page rather than a silent CREATE that duplicates the frame.
- Component and component-set `description` **is** writable and durable — use it for
  per-component metadata, and keep it current (rubric C14).

---

## Non-negotiable rules

1. **Never invent a token value.** No match in Semantic or Primitives → stop and report.
2. **Component variables are aliases only.** A raw hex or number in the Component
   collection is a bug.
3. **Semantic first; Primitives when justified.** Aliasing a Primitive is legitimate when
   no purpose-level meaning exists (alpha tints, one-off decorative values). It requires
   a written reason in the variable description and is flagged `primitive-justified`,
   not `semantic-gap`. See token-rules.md.
4. **Match the file.** Discover the file's conventions — collection modes, token naming,
   scope habits — and follow them. Deviate only where provably safe, and say so in the
   report. This outranks every default in this skill.
5. **Both modes always rendered and always validated.** Contrast is computed per mode,
   with **alpha composited against the actual backdrop** before the ratio. Reading raw
   RGB on an alpha token reports a pass where there is a failure.
6. **Typography: one strategy per node.** Bind a text style when the whole ramp is fixed.
   Bind Typography variables when a single axis varies by state. Never mix on one node.
   Record which is in use in the spec block.
7. **Orthogonal states are separate properties.** If two states co-occur in reality, they
   are not values of one variant.
7a. **Parts are resolved before the parent is documented.** A part discovered mid-build
   stops the run — report what it invalidates, fix the part, re-run those sections. A
   parent is never `ready-for-dev` while a part has blockers.
8. **Never delete.** Deprecate: rename with `⚠️ deprecated · `, set the description,
   report it. Exception: nodes this skill created that are now dead — remove and report.
9. **No detached instances in the handoff frame.**
10. **Incremental writes.** One section per call; validate IDs between calls.
11. **Never auto-apply breaking changes.**
12. **Every text node uses one of the four recipes in text-layout.md.** A `FILL` text node
    requires a `FIXED`-width ancestor — verify it, never assume it. A container that hugs
    horizontally while holding a `FILL` child is always a bug.
13. **Every write script verifies its own returned node IDs and throws on failure.**
    Not at the end of the phase — at the end of the write. Scripts are atomic, so a thrown
    assertion costs nothing and leaves the file clean. See
    [post-write-verification.md](references/post-write-verification.md). If a rubric blocker
    ever fires for something a write should have caught, the assertion was incomplete — fix
    the assertion, not just the node.
14. **Read figma-api-pitfalls.md before writing.** Several constraints there produce output
    that looks fine and is broken.

---

## Output contract

```
figma-specsheet · Tabs · RE-AUDIT

  handoff frame   72:1180        sections   13 of 13
  component       48:210          tokens     14 bound · 0 hardcoded
  modes           Light ✓ Dark ✓   contrast   22 checks · 19 pass · 1 fail · 2 exempt

  CHANGED SINCE v1.1.0 (2)
    tab         hardcoded 32px height, radius 6  →  size/32 + radius/6
    unread      value of `state`                 →  boolean + dot

  BLOCKERS (1)
    E2   unread tint vs surface · Light 2.1:1 · Dark 2.4:1 · needs 3:1
         sole indicator of the state — WCAG 1.4.11

  WARNINGS (2)
    C13  tabs/tab/unread-hover is bound to a fill but named as a hover token
    C14  its description still describes a treatment two revisions old

  INFO (1)
    C6b  tabs/tab/background/unread → color/blue/500/30 · primitive-justified

  needsHumanReview: 1 blocker — do not run read-figma-component yet.
```

Alongside the prose, emit the JSON block from audit-rubric.md so CI can gate on it and the
next run can diff it. Close every report with the calibration note — findings may be
deliberate, and a downgrade gets recorded in the config rather than re-argued.

**If `needsHumanReview` is non-empty, say so and stop.**
