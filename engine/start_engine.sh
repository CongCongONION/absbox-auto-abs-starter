#!/usr/bin/env bash
# Start a LOCAL Hastructure engine for absbox 0.50.3 (engine 0.50.2).
# Version rule (AbsBox docs): the MINOR version of absbox and the engine
# must match (0.50.x with 0.50.x). The public engine at absbox.org was
# returning 502 Bad Gateway on 2026-11-10, so run it locally instead.
set -e
cd "$(dirname "$0")"

if [ ! -f hastructure ]; then
  echo "Downloading Hastructure 0.50.2 (Linux)..."
  curl -sL -o hastructure \
    https://github.com/absbox/Hastructure/releases/download/v0.50.2/Hastructure-0.50.2-Linux-ghc-9.8.2
  chmod +x hastructure
fi
if [ ! -f config.yml ]; then
  curl -sL -o config.yml \
    https://raw.githubusercontent.com/absbox/Hastructure/master/config.yml
fi
echo "Engine on http://localhost:8081  (Ctrl+C to stop)"
./hastructure
