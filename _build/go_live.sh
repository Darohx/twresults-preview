#!/usr/bin/env bash
# TW Results go-live (PREPARED, NOT RUN). Usage:
#   bash _build/go_live.sh https://formspree.io/f/XXXXXXXX
# What it does:
#   1. Puts the Formspree endpoint into _build/build.py (preview repo) and commits it there.
#   2. Copies the source to a clean folder, runs the --live build (no noindex, robots allow-all, 404 base "/").
#   3. Writes CNAME = twresults.com, creates the NEW production repo Darohx/twresults.com, pushes, and turns on GitHub Pages.
# It does NOT touch DNS. Do the Namecheap steps (Namecheap_GoLive_Steps.txt) after this, then tick "Enforce HTTPS" once the certificate is issued.
set -euo pipefail
ENDPOINT="${1:-}"
[[ "$ENDPOINT" =~ ^https://formspree\.io/f/[A-Za-z0-9]+$ ]] || { echo "Give the Formspree endpoint, e.g. https://formspree.io/f/abcd1234"; exit 1; }
SRC="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/workspace/twresults-live
PROD_REPO=Darohx/twresults.com
ID=(-c user.name=Darohx -c user.email=dan@twresults.com)

# 1. Endpoint into the source
sed -i "s#^FORM_ENDPOINT = \"\[FORM ENDPOINT\]\"#FORM_ENDPOINT = \"$ENDPOINT\"#" "$SRC/_build/build.py"
grep -q "^FORM_ENDPOINT = \"$ENDPOINT\"" "$SRC/_build/build.py" || { echo "Endpoint not set in build.py"; exit 1; }
( cd "$SRC" && python3 _build/build.py && git add -A && git "${ID[@]}" commit -qm "Formspree endpoint set" && git push -q origin main )

# 2. Live build in a clean copy
rm -rf "$OUT"; mkdir -p "$OUT"
cp -a "$SRC/." "$OUT/" && rm -rf "$OUT/.git" "$OUT/_build/__pycache__"
( cd "$OUT" && python3 _build/build.py --live )
grep -q 'noindex' "$OUT/index.html" && { echo "noindex still in live build, stopping"; exit 1; } || true
grep -q 'Disallow: /$' "$OUT/robots.txt" && { echo "robots still disallow-all, stopping"; exit 1; } || true
grep -rq '\[FORM ENDPOINT\]' "$OUT"/*.html "$OUT"/*/index.html && { echo "endpoint placeholder still present"; exit 1; } || true
grep -rq "07944" --include=*.html "$OUT" && { echo "Found 07944 in the pages, stopping"; exit 1; } || true
echo "twresults.com" > "$OUT/CNAME"
rm -rf "$OUT/_build"   # build tooling is not published on production

# 3. New production repo + Pages
cd "$OUT"
git init -q -b main && git add -A && git "${ID[@]}" commit -qm "TW Results live site"
gh repo view "$PROD_REPO" >/dev/null 2>&1 || gh repo create "$PROD_REPO" --public --description "twresults.com (live)"
git remote add origin "https://github.com/$PROD_REPO.git"
git push -q -u origin main
gh api -X POST "repos/$PROD_REPO/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 || true
gh api -X PUT "repos/$PROD_REPO/pages" -f cname=twresults.com >/dev/null
echo "Pushed to $PROD_REPO. Next: Namecheap DNS steps, then enable 'Enforce HTTPS' in repo Settings > Pages once the certificate shows."
