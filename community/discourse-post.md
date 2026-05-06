我把刚才本机解决 Codex 通知漏提醒的问题整理成了一个小工具：

https://github.com/constansino/codex-attention-notifier

也发到了 openai/codex 的讨论区：

https://github.com/openai/codex/discussions/21354

它解决的问题是：Codex 默认的 turn 结束通知不够覆盖所有“需要你回来处理”的场景。比如任务跑到一半要权限批准，或者准备执行 `sudo xcodebuild -license accept`、安装器、`softwareupdate` 这类很可能需要输入管理员密码的命令，如果窗口不在前台，很容易误以为 Codex 还在跑，其实它已经卡在等人。

效果：

- Codex 发出 `PermissionRequest` 时弹 macOS 系统通知。
- 在执行常见需要人工介入的命令前提前提醒，例如 `sudo`、`xcodebuild -license`、`xcodebuild -runFirstLaunch`、`.pkg` installer、`softwareupdate`、AppleScript administrator privileges。
- 普通命令不提醒，不会每次 `ls`、`git`、build 都弹。
- 只做通知和日志，不会自动批准、拒绝或改写 Codex 的工具调用。
- 日志写到 `~/.codex/logs/codex-attention-notifier.log`。

安装方法：

```bash
git clone https://github.com/constansino/codex-attention-notifier.git
cd codex-attention-notifier
python3 install.py
```

安装后重启 Codex Desktop，或者开一个新的 Codex session，让新的 hooks 配置生效。

可以用这个命令测试，不会真的运行 sudo，只是模拟 Codex hook 输入：

```bash
printf '%s\n' '{"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":"'"$PWD"'","tool_input":{"command":"sudo xcodebuild -license accept"}}' \
  | python3 ~/.codex/hooks/codex_attention_notify.py
```

如果正常，会看到 macOS 通知，也能看到日志：

```bash
tail -n 5 ~/.codex/logs/codex-attention-notifier.log
```

限制也说清楚：这不是官方一等功能，只是基于 Codex hooks 的实用补丁。对于“子进程已经跑起来后才卡在 stdin/password”的情况，Codex 目前还没有稳定的等待输入事件 hook，所以这个工具是通过执行前识别高风险命令来兜住常见场景。
