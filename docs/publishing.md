# Publishing

The repo is initialised with history and passes its own checks. To put it on GitHub:

```bash
cd "Skills/figma-specsheet"

# with the gh CLI
gh repo create figma-specsheet --public --source=. --remote=origin \
  --description "Build and audit component handoff documentation inside Figma — anatomy, modes, states, tokens, accessibility." \
  --push

# or manually
git remote add origin git@github.com:alfremiranda/figma-specsheet.git
git push -u origin main
```

## Suggested repo settings

**Topics** — `figma`, `design-systems`, `design-tokens`, `handoff`, `claude`, `claude-skill`,
`accessibility`, `documentation`, `figma-plugin-api`

**About** — "A Claude skill that builds and audits component handoff documentation inside
Figma: anatomy, modes, states, tokens, accessibility, do/don't."

## Cutting a release

```bash
./scripts/package.sh                      # → dist/figma-specsheet-<version>.skill
gh release create v3.1.0 dist/*.skill --notes-file <(sed -n '/^## v3.1.0/,/^## v3.0/p' CHANGELOG.md)
```

`scripts/package.sh` reads the version from the first `## vX.Y[.Z]` heading in
`CHANGELOG.md`, so bump the changelog first and the archive name follows.

> Running `package.sh` inside a Cowork-mounted workspace fails at the final rename —
> `zip` writes a temp file and cannot replace the target across that mount. Run it from a
> normal terminal on your machine, or let the CI `package` job build the artifact.

## Before the first push

- [ ] Add a real render at `docs/handoff-frame.png` and reference it in the README
- [ ] Confirm `python3 scripts/check.py` passes
