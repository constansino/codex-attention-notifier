I published a small hook-based workaround that may help with this class of "Codex is blocked waiting for me" problems on macOS:

https://github.com/constansino/codex-attention-notifier

It uses Codex hooks to send a native macOS notification for `PermissionRequest` events and a pre-flight warning for commands that are likely to need manual input, such as `sudo`, `xcodebuild -license`, installers, and `softwareupdate`.

It is not a first-party fix for the missing notification path described in this issue, and it cannot detect every child process that blocks on stdin after it has already started. It is a practical workaround for the common approval/password cases while the native notification behavior is still being improved.

More details:

https://github.com/openai/codex/discussions/21354
