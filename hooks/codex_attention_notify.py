#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


LOG_PATH = Path.home() / ".codex" / "logs" / "codex-attention-notifier.log"


def shorten(text, limit=180):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def applescript_string(text):
    return str(text).replace("\\", "\\\\").replace('"', '\\"')


def notify_macos(title, message, subtitle=None):
    script = (
        "display notification "
        + f'"{applescript_string(message)}" '
        + f'with title "{applescript_string(title)}"'
    )
    if subtitle:
        script += f' subtitle "{applescript_string(subtitle)}"'
    script += ' sound name "Glass"'

    subprocess.run(
        ["/usr/bin/osascript", "-e", script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=5,
        check=False,
    )


def notify(title, message, subtitle=None):
    if sys.platform == "darwin":
        notify_macos(title, message, subtitle)
        return

    if sys.platform.startswith("linux"):
        subprocess.run(
            ["notify-send", title, message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
        return

    print(f"{title}: {message}", file=sys.stderr)


def read_input():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception as exc:
        return {"_parse_error": str(exc)}


def log_event(payload, title, message):
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        tool_input = payload.get("tool_input", {})
        record = {
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "event": payload.get("hook_event_name"),
            "tool": payload.get("tool_name"),
            "cwd": payload.get("cwd"),
            "title": title,
            "message": message,
            "command": tool_input.get("command") if isinstance(tool_input, dict) else None,
        }
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def should_warn_before_tool(command):
    compact = re.sub(r"\s+", " ", str(command or "")).strip()
    if not compact:
        return False

    patterns = [
        r"(^|[;&|]\s*)sudo(\s|$)",
        r"\bxcodebuild\b.*\b(-license|runFirstLaunch)\b",
        r"\binstaller\b.*\b-pkg\b",
        r"\bsoftwareupdate\b.*\b(--install|-i|--install-rosetta)\b",
        r"\bspctl\b.*\b(--master-disable|--add|--enable|--disable)\b",
        r"\bsecurity\b.*\b(add-trusted-cert|authorizationdb|set-key-partition-list)\b",
        r"\bosascript\b.*\badministrator privileges\b",
        r"\blaunchctl\b.*\b(bootstrap|bootout|enable|disable|kickstart)\b.*\b(system|/Library)\b",
    ]
    return any(re.search(pattern, compact) for pattern in patterns)


def main():
    payload = read_input()
    event = payload.get("hook_event_name", "Codex")
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    command = tool_input.get("command") if isinstance(tool_input, dict) else ""
    reason = tool_input.get("description") if isinstance(tool_input, dict) else ""

    if event == "PermissionRequest":
        title = "Codex needs attention"
        message = shorten(reason or command or f"{tool} is requesting approval")
        notify(title, message, subtitle=tool or None)
        log_event(payload, title, message)
        return 0

    if event == "PreToolUse":
        if not should_warn_before_tool(command):
            return 0
        title = "Codex may need your password"
        message = shorten(command or f"{tool} is about to run")
        notify(title, message, subtitle=tool or None)
        log_event(payload, title, message)
        return 0

    title = "Codex needs attention"
    message = shorten(f"{event} {tool}".strip())
    notify(title, message)
    log_event(payload, title, message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

