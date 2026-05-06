#!/usr/bin/env python3
"""
CoolTerminal - System info display for Windows terminal.
Runs automatically on terminal open.

MIT License - https://github.com/nthung-bot/Coolterminal
"""

import os
import sys

# Support running as a PyInstaller bundle or plain script
if getattr(sys, "frozen", False):
    _pkg_dir = sys._MEIPASS
else:
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))

if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from coolterm_pkg.config_manager import (
    load_config, save_config, get_accent, enable_ansi,
    RESET, BOLD, DIM, COLOR_CODES,
)
from coolterm_pkg.sysinfo import collect
from coolterm_pkg.updater import check_and_prompt


# Windows 4-pane flag logo (visible width: 26 chars per line)
def _logo(accent):
    B = f"{accent}██████████{RESET}"
    SP = "  "
    pad = "  "
    line = f"{pad}{B}{SP}{B}{pad}"
    blank = " " * 26
    return [line, line, line, line, blank, line, line, line, line]


def run():
    enable_ansi()
    cfg = load_config()

    if not cfg.get("enabled", True):
        return

    accent = get_accent(cfg)
    info = collect()

    user = info["username"]
    host = info["hostname"]
    sep = DIM + "─" * (len(user) + len(host) + 1) + RESET

    label_w = 13  # fixed width for label column (including colon)

    def row(label, value):
        return f"{accent}{label:<{label_w}}{RESET}{value}"

    info_lines = [
        f"{BOLD}{accent}{user}{RESET}@{BOLD}{accent}{host}{RESET}",
        sep,
        row("OS:",         info["os"]),
        row("Build:",      info["build"]),
        row("Uptime:",     info["uptime"]),
        row("Shell:",      info["shell"]),
        row("Resolution:", info["res"]),
        row("CPU:",        info["cpu"]),
        row("GPU:",        info["gpu"]),
        row("RAM:",        info["ram"]),
        row("Disk:",       info["disk"]),
    ]

    logo = _logo(accent)
    print()
    for i in range(max(len(logo), len(info_lines))):
        left  = logo[i]       if i < len(logo)       else " " * 26
        right = info_lines[i] if i < len(info_lines) else ""
        print(f"  {left}   {right}")
    print()

    check_and_prompt(cfg, save_config, accent, RESET, BOLD)


if __name__ == "__main__":
    run()
