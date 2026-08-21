#!/usr/bin/env bash
# Build the distributable .skill archive (a zip of the skill folder).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="figma-specsheet"
VERSION="$(grep -m1 -oE '^## v[0-9]+\.[0-9]+(\.[0-9]+)?' "$ROOT/CHANGELOG.md" | sed 's/^## v//' || true)"
VERSION="${VERSION:-0.0.0}"

OUT="$ROOT/dist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$OUT" "$STAGE/$NAME"
cp "$ROOT/SKILL.md" "$ROOT/CHANGELOG.md" "$ROOT/README.md" "$ROOT/LICENSE" "$STAGE/$NAME/"
cp -R "$ROOT/references" "$STAGE/$NAME/references"

ARCHIVE="$OUT/$NAME-$VERSION.skill"
rm -f "$ARCHIVE"
( cd "$STAGE" && zip -qr "$ARCHIVE" "$NAME" )

echo "built $ARCHIVE"
