# codex-sessions

一个常驻终端的 Codex 本机会话浏览器。选中会话后复制 `codex resume` 命令，列表保持打开，方便在另一个终端继续工作。

使用 Python 标准库实现，无第三方 Python 依赖。保留紧凑的单行列表，相同工作路径使用固定颜色。

```text
Codex 会话列表 · 每 5 秒刷新 · 同路径同色 · 跟随开
↑↓ 选择  Enter 复制命令  / 搜索  a 归档  s 来源  n 改名
范围：含已归档 | CLI + IDE | 3 条 | 搜索：
最近一轮：发起时间 → 完成时间   f 开关自动跟随
11-10 15:10 → 11-10 15:11  历史  cli     修复登录问题
11-10 15:09 → 未结束       历史  vscode  整理项目文档
11-09 17:34 → 11-09 17:40  归档  cli     调整列表样式

标题：修复登录问题
目录：/path/to/project
codex resume <SESSION_ID> --cd /path/to/project
发起 11-10 15:10:00  完成 11-10 15:11:20  耗时 80.0s
```

以上为虚拟示例，实际颜色由终端显示。

## 功能

| 能力 | 说明 |
| --- | --- |
| 常驻会话列表 | 选择或复制后列表不关闭，每 5 秒刷新一次 |
| 跨项目浏览 | 读取本机索引中的 CLI 和 IDE（`vscode` 来源）交互会话 |
| 归档浏览 | 可同时显示已归档会话，并随时切换范围 |
| 搜索 | 按标题、完整工作目录、会话 ID 和来源匹配；多个词以空格分隔 |
| 路径配色 | 相同规范化工作路径始终使用同一种颜色；颜色数量有限，不同路径可能同色 |
| 复制打开命令 | Enter 复制完整命令，在另一个终端粘贴执行；包括原工作目录 |
| 会话重命名 | `n` 或 F2 编辑标题，通过 Codex 官方 `thread/name/set` 接口保存 |
| 发起与完成时间 | 显示最近一轮实际执行的开始、完成时间，底部精确到秒并显示已记录的耗时 |
| 状态区分 | 区分已完成、未结束、已中断、失败，以及缺少时间信息的未知状态 |
| 自动跟随高亮 | 新执行开始或完成后，切换高亮并滚动到对应会话；`f` 可开关 |
| 命令行输出 | 支持 JSON 元数据和按会话 ID 输出打开命令 |

## 环境要求

- macOS；剪贴板使用系统自带的 `pbcopy`。
- Python 3.9 或更新版本，包含 `curses` 和 `sqlite3`。
- 已安装并运行过 Codex CLI，`codex` 可从 PATH 中调用。
- 支持颜色的交互终端，建议使用至少 100 列显示较长标题；最低 50 列、13 行。

当前实现已在 Codex CLI **0.167.0** 的本地数据结构下验证。历史读取依赖 Codex 的本地 SQLite 索引和 JSONL 生命周期事件，不是跨设备云同步客户端。

## 安装

```bash
git clone https://github.com/Joker311223/codex-sessions.git
cd codex-sessions
./install.sh
```

默认安装到 `~/.local/bin/codex-sessions`。如果该目录尚未加入 PATH，可在 `~/.zshrc` 中添加：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

然后重新打开终端，或执行 `source ~/.zshrc`。

也可直接从仓库启动：

```bash
python3 ./codex-sessions --archived
```

自定义安装目录：

```bash
CODEX_SESSIONS_BIN_DIR="$HOME/bin" ./install.sh
```

## 使用

### 浏览全部本地交互会话，包括归档

```bash
codex-sessions --archived
```

### 仅浏览 CLI 来源

```bash
codex-sessions --cli-only --archived
```

### 默认只看未归档会话

```bash
codex-sessions
```

### 使用指定 Codex 数据目录

```bash
codex-sessions --home /path/to/.codex --archived
```

也支持 `CODEX_HOME` 环境变量；`--home` 优先。

### 输出 JSON 元数据

```bash
codex-sessions --archived --json
```

JSON 输出的是索引元数据；执行时间从日志按需读取，当前不包含在 JSON 输出中。

### 输出某条会话的打开命令

```bash
codex-sessions --command <SESSION_ID>
```

用真实会话 ID 替换 `<SESSION_ID>`。该操作只打印命令，不执行。

## 快捷键

| 按键 | 操作 |
| --- | --- |
| ↑ / ↓ 或 `k` / `j` | 选择会话 |
| PgUp / PgDn | 上下翻页 |
| Enter | 复制选中会话的打开命令，列表保持显示 |
| `/` | 输入搜索词；Enter 或 Esc 结束输入 |
| `a` | 切换是否包含已归档会话 |
| `s` | 切换全部交互来源 / 仅 CLI |
| `n` / F2 | 重命名选中会话 |
| `f` | 开关自动跟随高亮，默认开启 |
| `r` | 立即刷新 |
| `q` / Esc | 退出；如果曾复制命令，退出时会再打印最后复制的命令 |

### 修改标题

1. 选中会话，按 `n` 或 F2。
2. 输入新标题。可按 Ctrl+U 清空原文本，Backspace 删除字符。
3. Enter 保存，Esc 取消。

标题允许 1–200 个字符，不支持换行或控制字符。保存的是 Codex 会话名，不是本工具的临时别名；列表会优先显示新名字。保存通过本机 `codex app-server` 的元数据接口完成，不会启动模型执行任务。

### 自动跟随的规则

- 观察到新的 `task_started` 或 `task_complete` 事件时，自动选中对应会话。
- 多条会话同时发生变化时，选择事件时间最新的一条。
- 默认以 5 秒间隔检测，不保证毫秒级实时性。
- 手动浏览后保持选择，直到下一次新执行事件。
- 进入搜索或改名输入时，延迟切换，输入结束后再跟随。
- 新事件目标不符合当前搜索时，会清空搜索，让目标行可见。
- 不会切换到当前来源或归档范围之外的会话。
- 刚打开列表时建立基线，不因旧历史事件反复跳动。
- 修改标题、普通日志输出或元数据更新时间变化，不会单独触发跟随。

按 `f` 关闭后，即可固定手动选择。

## 时间与状态说明

列表显示的是**最近一轮执行**的发起与完成时间，不是会话创建时间，也不是 SQLite 中的最后更新时间。

- 优先使用生命周期事件中的 `started_at`、`completed_at` 和 `duration_ms`。
- 旧格式完成事件没有 `completed_at` 时，使用该完成事件自身的时间戳。
- 有开始记录、没有结束记录时显示「未结束」，不据此断言进程仍在运行。
- 中断和失败不会当作正常执行完成。
- 日志不存在、旧记录缺少生命周期信息，或近期日志片段不足以确认时显示「未知」。

时间以本机时区显示。为控制读取成本，只检查日志末尾最多 2 MiB，并按文件变更缓存结果。

**一轮执行完成并不代表整项业务需求已经完成。** 同一会话可以继续发起后续轮次。

## 数据与行为

- 读取 `CODEX_HOME` 下版本号最高的 `state_*.sqlite`；默认目录是 `~/.codex`。
- 索引使用只读连接，排除内部子代理和 `exec` 非交互记录。
- 不上传会话，不自动执行复制的命令。
- 只有主动保存新标题时，才调用官方改名接口修改会话元数据。
- 已归档会话的打开命令包含 `codex unarchive <ID> && codex resume <ID> ...`；**只有你粘贴执行后才会取消归档**。
- 不支持系统剪贴板时，退出列表后仍会打印最后选中的复制命令。

Codex 内部索引、日志格式和实验性 app-server 接口未来可能变化。升级后若出现读取或改名错误，可先确认 `codex --version`，再检查兼容性。

## 开发与测试

全部测试使用临时目录、虚拟会话和模拟元数据服务，不会修改真实会话。

```bash
python3 -m unittest discover -s tests -v
```

参考：[Codex 开发者命令](https://learn.chatgpt.com/docs/developer-commands)、[Codex App Server](https://learn.chatgpt.com/docs/app-server)。

## 更新与卸载

更新：

```bash
git pull --ff-only
./install.sh
```

正在运行的列表不会自动重新载入脚本，更新后按 `q` 退出再启动。

卸载：

```bash
rm "$HOME/.local/bin/codex-sessions"
```

如果使用了自定义安装目录，请删除对应文件。卸载不会删除 Codex 的会话记录。
