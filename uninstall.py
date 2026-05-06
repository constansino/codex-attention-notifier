#!/usr/bin/env python3
import json
import os
from pathlib import Path


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
HOOK_DEST = CODEX_HOME / "hooks" / "codex_attention_notify.py"
HOOKS_JSON = CODEX_HOME / "hooks.json"


def remove_managed_entries(entries):
    cleaned = []
    for entry in entries:
        hooks = entry.get("hooks", [])
        kept_hooks = [
            hook
            for hook in hooks
            if not str(hook.get("command", "")).endswith("codex_attention_notify.py")
        ]
        if kept_hooks:
            entry = dict(entry)
            entry["hooks"] = kept_hooks
            cleaned.append(entry)
    return cleaned


def main():
    if HOOKS_JSON.exists():
        with HOOKS_JSON.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        hooks = data.get("hooks", {})
        for event in ("PermissionRequest", "PreToolUse"):
            if event in hooks:
                hooks[event] = remove_managed_entries(hooks[event])
                if not hooks[event]:
                    del hooks[event]
        with HOOKS_JSON.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(f"Updated hooks config: {HOOKS_JSON}")

    if HOOK_DEST.exists():
        HOOK_DEST.unlink()
        print(f"Removed hook: {HOOK_DEST}")

    print("codex_hooks was left enabled because other hooks may depend on it.")


if __name__ == "__main__":
    main()

