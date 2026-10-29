#!/bin/sh
# check.sh — verify every template obeys the vault rules. POSIX sh, no deps.
# Run from anywhere; exits non-zero if any template fails. Styling is each
# template's own business — this only enforces structure, not taste.
# ponytail: grep-based, not an HTML parser. Good enough; swap for a parser only
# if a template ever defeats these line checks.

cd "$(dirname "$0")" || exit 2
fail=0

for dir in templates/*/; do
  slug=${dir#templates/}; slug=${slug%/}
  tfail=0
  note() { echo "  FAIL $slug: $1"; fail=1; tfail=1; }

  # 1. external stylesheet exists (no per-template inline theming)
  [ -f "${dir}style.css" ] || note "no style.css"

  # per content page
  for f in "$dir"*.html; do
    [ -f "$f" ] || continue
    b=${f##*/}
    grep -q 'rel="stylesheet"' "$f"      || note "$b: no external stylesheet link"
    grep -q '<style' "$f"                && note "$b: has inline <style>"
    grep -q 'data-slot=' "$f"            || note "$b: no data-slot"
    grep -q 'src="../../edit.js"' "$f"   || note "$b: missing edit.js hook"
  done

  # 2. no placeholder filler — themed copy only
  grep -riq 'lorem ipsum' "$dir" && note "contains lorem ipsum"

  # 3. offline-safe: no remote assets. Allow only SVG/XML namespace URLs (w3.org).
  if grep -rohE 'https?://[^"'"'"' )>]+' "$dir" | grep -vE 'w3\.org|purl\.org' | grep -q .; then
    note "remote http(s) reference"
  fi
  grep -rEq '(@import|//fonts\.|//cdn\.|\.cdn\.)' "$dir" && note "remote @import/CDN"

  [ "$tfail" -eq 0 ] && echo "ok   $slug"
done

# 4. showroom registration: every non-underscore slug listed in index.html
for dir in templates/*/; do
  slug=${dir#templates/}; slug=${slug%/}
  case $slug in _*) continue ;; esac
  grep -q "\"$slug\"" index.html || { echo "  FAIL $slug: not registered in index.html"; fail=1; }
done

echo "---"
[ "$fail" -eq 0 ] && echo "PASS: all templates conform" || echo "FAIL: see above"
exit $fail
