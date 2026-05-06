I ran into a small but painful Codex UX gap on macOS: turn-complete notifications are useful, but they do not cover every "Codex is waiting for me" moment. The easiest one to miss is a long-running task that reaches an approval prompt or starts a command that is likely to ask for an administrator password, such as `sudo xcodebuild -license accept`.

I put together a small hook-based workaround:

https://github.com/constansino/codex-attention-notifier

What it does:

- Sends a native macOS notification for Codex `PermissionRequest` hook events.
- Sends a warning before shell commands that commonly require manual attention, including `sudo`, `xcodebuild -license`, `xcodebuild -runFirstLaunch`, `.pkg` installers, `softwareupdate`, and AppleScript administrator prompts.
- Ignores normal shell commands, so it does not beep on every `ls`, `git`, or build command.
- Logs notification events under `~/.codex/logs/codex-attention-notifier.log`.
- Does not approve, deny, or modify any tool call.

Install:

```bash
git clone https://github.com/constansino/codex-attention-notifier.git
cd codex-attention-notifier
python3 install.py
```

Then restart Codex Desktop or open a new Codex session so the hook config is loaded.

Quick test without actually running `sudo`:

```bash
printf '%s\n' '{"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"sudo xcodebuild -license accept"}}' \
  | python3 ~/.codex/hooks/codex_attention_notify.py
```

This is not a first-party fix. It is just a practical local workaround built on Codex hooks. In particular, it does not solve the deeper case where a child process is already running and only later blocks on stdin; for that, Codex would need a stable "terminal interaction / waiting for input" attention event. This hook handles the common password case by notifying before high-risk commands run.

Related threads I found while looking into this:

- #3962
- #11097
- #17716

