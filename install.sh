#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "$0")" && pwd)"
bin_dir="${CODEX_SESSIONS_BIN_DIR:-$HOME/.local/bin}"
command -v python3 >/dev/null || { echo '请先安装 Python 3.9 或更新版本。' >&2; exit 1; }
python3 -c 'import curses, sqlite3' || { echo 'Python 缺少 curses 或 sqlite3。' >&2; exit 1; }
command -v codex >/dev/null || { echo '请先安装 Codex CLI，并确保 codex 在 PATH 中。' >&2; exit 1; }
mkdir -p "$bin_dir"
install -m 755 "$project_dir/codex-sessions" "$bin_dir/codex-sessions"
printf '已安装：%s/codex-sessions\n' "$bin_dir"
case ":$PATH:" in
  *":$bin_dir:"*) printf '运行：codex-sessions --archived\n' ;;
  *) printf '请将以下目录加入 shell 的 PATH：%s\n' "$bin_dir" ;;
esac
