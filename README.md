# Codex Attention Notifier

Native macOS notifications for Codex moments that need human attention.

Codex already supports turn-complete notifications and a hooks engine, but the default setup can still be easy to miss when a task blocks on an approval prompt or a command that is likely to ask for an administrator password. This small hook adds a focused "needs attention" notification layer.

## What It Does

- Sends a macOS notification when Codex emits a `PermissionRequest` hook.
- Warns before shell commands that commonly require manual action, such as `sudo`, `xcodebuild -license`, `xcodebuild -runFirstLaunch`, `.pkg` installers, `softwareupdate`, and AppleScript administrator prompts.
- Ignores normal shell commands, so it does not notify on every `ls`, `git`, or build command.
- Logs notification events to `~/.codex/logs/codex-attention-notifier.log` for debugging.
- Does not approve, deny, or modify any Codex tool call.

## Why This Exists

The failure mode is simple: Codex can run for a while, then the terminal or app is unfocused while it waits for a user decision or a password prompt. If no notification fires, the session appears to be "still running" even though it is actually blocked.

This project is a practical workaround for that gap. It uses Codex hooks instead of changing Codex itself.

## Install

```bash
git clone https://github.com/constansino/codex-attention-notifier.git
cd codex-attention-notifier
python3 install.py
```

Then restart Codex Desktop or open a new Codex session so the new hook configuration is loaded.

## Test

This test does not run `sudo`. It only simulates the hook input:

```bash
printf '%s\n' '{"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"sudo xcodebuild -license accept"}}' \
  | python3 ~/.codex/hooks/codex_attention_notify.py
```

You should see a macOS notification and a log entry:

```bash
tail -n 5 ~/.codex/logs/codex-attention-notifier.log
```

## Files Installed

- `~/.codex/hooks/codex_attention_notify.py`
- `~/.codex/hooks.json` entries for `PermissionRequest` and `PreToolUse`
- `[features].codex_hooks = true` in `~/.codex/config.toml`

The installer creates timestamped backups before editing existing Codex config files.

## Uninstall

```bash
python3 uninstall.py
```

This removes the hook entries managed by this project and deletes the installed hook script. It does not disable Codex hooks globally, because other hooks may use the same feature.

## Notes

This is a notifier, not a permission system. It deliberately returns success without a decision, so Codex continues to handle approvals normally.

For child-process password prompts such as `sudo Password:`, Codex does not currently expose a stable "the process is now waiting for stdin" hook. This project handles that class by warning before commands that are very likely to need user input.

