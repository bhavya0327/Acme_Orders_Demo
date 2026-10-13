#!/usr/bin/env bash
# Serve both builds side by side:  5.39 -> http://localhost:4539   5.40 -> http://localhost:4540
HERE="$(cd "$(dirname "$0")" && pwd)"
python3 -m http.server 4539 --directory "$HERE/builds/5.39" >/dev/null 2>&1 & P1=$!
python3 -m http.server 4540 --directory "$HERE/builds/5.40" >/dev/null 2>&1 & P2=$!
echo "Acme Orders 5.39 -> http://localhost:4539/#/login"
echo "Acme Orders 5.40 -> http://localhost:4540/#/login"
trap 'kill $P1 $P2 2>/dev/null' EXIT INT TERM
wait
