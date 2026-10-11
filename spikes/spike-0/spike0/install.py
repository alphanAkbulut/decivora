"""Hook kurulumu: YALNIZ verilen projenin .claude/settings.local.json dosyasi.

~/.claude (kullanici duzeyi) ayarina dokunulmaz. Mevcut dosya once yedeklenir.
Hook komutu dosya adi `spike0_hook.py` ile isaretlenir; uninstall bunu kullanir.
"""
import json
import os
import shlex
import shutil
import sys
import time

from .db import HERE, data_dir

MARK = "spike0_hook.py"
EVENTS = ["SessionStart", "UserPromptSubmit", "Stop", "SessionEnd"]
HOOK_PATH = os.path.join(HERE, "bin", MARK)


def _settings_path(project_dir):
    return os.path.join(os.path.abspath(project_dir), ".claude", "settings.local.json")


def _state_path():
    return os.path.join(data_dir(), "install.json")


def _load_state():
    try:
        with open(_state_path(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(s):
    with open(_state_path(), "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)


def hook_command():
    return "SPIKE0_DATA=%s %s %s" % (
        shlex.quote(data_dir()), shlex.quote(sys.executable), shlex.quote(HOOK_PATH))


def _strip(settings):
    hooks = settings.get("hooks", {})
    for ev in list(hooks):
        groups = []
        for g in hooks[ev]:
            g["hooks"] = [h for h in g.get("hooks", []) if MARK not in h.get("command", "")]
            if g["hooks"]:
                groups.append(g)
        if groups:
            hooks[ev] = groups
        else:
            del hooks[ev]
    if not hooks:
        settings.pop("hooks", None)
    return settings


def install(project_dir):
    path = _settings_path(project_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    state = _load_state()
    existed = os.path.exists(path)
    settings = {}
    if existed:
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
        bak = path + ".spike0-backup"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
    settings = _strip(settings)
    hooks = settings.setdefault("hooks", {})
    for ev in EVENTS:
        hooks.setdefault(ev, []).append(
            {"matcher": "", "hooks": [{"type": "command", "command": hook_command(), "timeout": 10}]})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    projects = state.setdefault("projects", {})
    projects.setdefault(os.path.abspath(project_dir), {"created_file": not existed,
                                                      "installed_at": time.time()})
    _save_state(state)
    return path


def uninstall(project_dir):
    path = _settings_path(project_dir)
    state = _load_state()
    info = state.get("projects", {}).pop(os.path.abspath(project_dir), {})
    if not os.path.exists(path):
        _save_state(state)
        return None
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
    settings = _strip(settings)
    if not settings and info.get("created_file"):
        os.remove(path)
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    _save_state(state)
    return path
