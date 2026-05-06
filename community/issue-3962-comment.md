I published a small hook-based workaround for macOS users who want a clearer "Codex needs attention" signal, not just turn-complete notifications:

https://github.com/constansino/codex-attention-notifier

It sends a native macOS notification for `PermissionRequest` hook events and warns before commands that are likely to require manual input (`sudo`, `xcodebuild -license`, installers, `softwareupdate`, etc.). It does not approve/deny anything; it only notifies and logs locally.

I also wrote a short discussion post with usage details here:

https://github.com/openai/codex/discussions/21354
