#!/bin/zsh
set -e
cd "$(dirname "$0")"
TASK_PYTHON="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
if [[ ! -x "$TASK_PYTHON" ]]; then TASK_PYTHON="$(command -v python3.12 || true)"; fi
if [[ -z "$TASK_PYTHON" || ! -x "$TASK_PYTHON" ]]; then
  print "Python 3.12 bulunamadı. Kurulu Codex runtime veya Python 3.12 gerekli."
  read "REPLY?Çıkmak için Enter: "
  exit 1
fi
exec "$TASK_PYTHON" -B -m apps.local_ui.server "$@"
