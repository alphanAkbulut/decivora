#!/bin/zsh
set -e
cd "$(dirname "$0")"
exec ./Decivora.command --environment test --port 53611 "$@"
