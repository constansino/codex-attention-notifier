更新一下：这个工具的默认安装方式已经改成只保留 `PermissionRequest` 通知，不再默认启用 `PreToolUse`。

原因是 Codex app 目前会把每一次 `PreToolUse` hook 都显示成“调用工具前”的记录。即使脚本内部判断普通命令后直接退出，UI 里还是会出现很多 hook 记录，实际体验会比较吵。

现在默认行为是：

- Codex 真正发出权限请求时通知。
- 不再每次 Bash 调用前运行 `PreToolUse`。
- 所以不会再刷“调用工具前”记录。

对应的限制是：`sudo Password:` 这类子进程密码输入等待，默认方案不再提前兜底。Codex 目前还没有稳定的“子进程已经进入等待 stdin/password 状态”的 hook；如果强行用 `PreToolUse` 做前置识别，就会带来上面说的 UI 噪音。

仓库 README 和安装脚本已经更新：

https://github.com/constansino/codex-attention-notifier

