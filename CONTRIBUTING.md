# Contributing

Thanks for looking. This skill is a set of rules that survived contact with a real Figma
file — the bar for adding to it is "this caught a bug", not "this seems like good practice".

## The most valuable contribution

**A new pitfall.** If you found a way the Figma Plugin API silently does something other
than what it reports — a binding that stores but renders a literal, a property that reads
correct but draws stale — that belongs in `references/figma-api-pitfalls.md`. Open an issue
with the [Pitfall report](.github/ISSUE_TEMPLATE/pitfall_report.md) template.

Every pitfall entry needs:

1. **Symptom** — what you saw, phrased the way you'd search for it
2. **Cause** — what the API actually did
3. **Reproduction** — the smallest script that triggers it
4. **Fix** — the working alternative
5. **Detection** — how a script can assert against it afterwards

Then add the symptom to the index at the top of the file, so it's findable by the thing
that went wrong rather than by the thing that caused it.

## Changing a rule

The 15 non-negotiables in `SKILL.md` and the checks in `references/audit-rubric.md` are
load-bearing. To change one, the PR needs to show the case where the current rule produces
a wrong result. Rule changes bump the **minor** version; new checks bump **patch**.

## Never publish a measurement of a real file

Worked examples explain failures. They do not carry data from the file the failure was found
in — no contrast ratios, variant or instance counts, node totals, token values, pixel
measurements, component names, node IDs, file keys, locales or handles.

This is not a formality. A skill like this gets developed against somebody's production
design system, and every number that survives into the repo tells its readers something
about that system which its owner never agreed to publish.

The mechanism is what teaches, and it survives generalisation intact:

> ✗ The width heuristic flagged 89 label columns; with the fix, 830 nodes and 0 issues.
> ✓ The width heuristic flagged dozens of correctly-designed label columns; with the fix, zero issues.

Both sentences make the same argument. Only one of them is about someone's file.

`scripts/check.py` enforces the two mechanical cases — live Figma file keys and real
`@handles`. The rest is a review question, and it is the first thing to look for in a PR
that adds an example.

## Style

- Reference files are loaded on demand — keep `SKILL.md` the index, push detail down.
- Every reference file that documents a class of failure starts with a **symptom index**.
- Write scripts in examples must include their own post-write verification. A snippet that
  writes without asserting teaches the wrong habit.
- Prose over bullets where the reasoning matters. The reader is deciding whether to trust
  the rule, not skimming for keywords.

## Versioning

[Semantic versioning](https://semver.org/). Record every change in `CHANGELOG.md` as a
numbered entry with the reason, not just the diff — the changelog is how the rules explain
themselves.

## Packaging a release

```bash
./scripts/package.sh          # → dist/figma-specsheet-<version>.skill
```

## Code of conduct

Be decent. Assume the other person hit a real problem.
