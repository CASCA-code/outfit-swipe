#!/usr/bin/env bash
# Publica en GitHub Pages (requiere OK explícito del usuario).
set -e
cd "$(dirname "$0")"
gh repo create CASCA-code/outfit-swipe --public --source . --remote origin --push \
  --description "Outfit swipe deck for style calibration"
gh api -X POST repos/CASCA-code/outfit-swipe/pages -f "source[branch]=main" -f "source[path]=/"
echo "URL: https://casca-code.github.io/outfit-swipe/"
