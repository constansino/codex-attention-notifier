#!/usr/bin/env python3
import json
import os
import shutil
from datetime import datetime
from pathlib import Path


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
PROJECT_ROOT = Path(__file__).resolve().parent
HOOK_SOURCE = PROJECT_ROOT / "hooks" / "codex_attention_notify.py"
HOOK_DEST = CODEX_HOME / "hooks" / "codex_attention_notify.py"
HOOKS_JSON = CODEX_HOME / "hooks.json"
CONFIG_TOML = CODEX_HOME / "config.toml"

MANAGED_COMMAND = f"/usr/bin/python3 {HOOK_DEST}"


def timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def backup(path):
    if path.exists():
        backup_path = path.with_name(f"{path.name}.bak.{timestamp()}")
        shutil.copy2(path, backup_path)
        return backup_path
    return None


def ensure_hook_script():
    HOOK_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK_SOURCE, HOOK_DEST)
    HOOK_DEST.chmod(0o755)


def hook_entry():
    return {
        "type": "command",
        "command": MANAGED_COMMAND,
        "timeout": 10,
    }


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


def ensure_hooks_json():
    if HOOKS_JSON.exists():
        backup(HOOKS_JSON)
        with HOOKS_JSON.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = {}

    hooks = data.setdefault("hooks", {})

    permission_entries = remove_managed_entries(hooks.get("PermissionRequest", []))
    permission_entries.append(
        {
            "matcher": "Bash|apply_patch|Edit|Write|mcp__.*",
            "hooks": [hook_entry()],
        }
    )
    hooks["PermissionRequest"] = permission_entries

    HOOKS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with HOOKS_JSON.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def ensure_codex_hooks_feature():
    CONFIG_TOML.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_TOML.exists():
        backup(CONFIG_TOML)
        text = CONFIG_TOML.read_text(encoding="utf-8")
    else:
        text = ""

    lines = text.splitlines()
    features_start = None
    for index, line in enumerate(lines):
        if line.strip() == "[features]":
            features_start = index
            break

    if features_start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["[features]", "codex_hooks = true"])
    else:
        insert_at = features_start + 1
        next_section = len(lines)
        for index in range(features_start + 1, len(lines)):
            if lines[index].strip().startswith("[") and lines[index].strip().endswith("]"):
                next_section = index
                break

        updated = False
        for index in range(features_start + 1, next_section):
            stripped = lines[index].strip()
            if stripped.startswith("codex_hooks"):
                lines[index] = "codex_hooks = true"
                updated = True
                break

        if not updated:
            lines.insert(insert_at, "codex_hooks = true")

    CONFIG_TOML.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ensure_hook_script()
    ensure_hooks_json()
    ensure_codex_hooks_feature()
    print(f"Installed hook: {HOOK_DEST}")
    print(f"Updated hooks config: {HOOKS_JSON}")
    print(f"Enabled codex_hooks in: {CONFIG_TOML}")
    print("Restart Codex Desktop or open a new Codex session to load the hooks.")


if __name__ == "__main__":
    main()
