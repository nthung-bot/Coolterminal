#!/usr/bin/env python3
"""
terconfig - CoolTerminal interactive configuration tool.

  terconfig              Open interactive config (S=save  X=exit)
  terconfig color <1-7>  Set accent color directly
  terconfig enabled <bool>  Enable or disable startup display
  terconfig reset        Reset to defaults
  terconfig help         Show this help
  terconfig /exit        Exit immediately (no output)

MIT License - https://github.com/nthung-bot/Coolterminal
"""

import msvcrt
import os
import sys
import time

if getattr(sys, "frozen", False):
    _pkg_dir = sys._MEIPASS
else:
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))

if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from coolterm_pkg.config_manager import (
    load_config, save_config, get_accent, enable_ansi,
    DEFAULT_CONFIG, COLOR_NAMES, COLOR_CODES,
    RESET, BOLD, DIM,
)

VERSION = "1.0.0"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clear():
    """Clear screen using ANSI (avoids spawning cmd.exe which triggers AutoRun)."""
    print("\033[2J\033[H", end="", flush=True)


def _ok(accent, msg):
    print(f"\n  {accent}Saved.{RESET}  {msg}")


def _err(msg):
    print(f"  \033[91m✗{RESET}  {msg}")


def _getkey():
    """Return a single lowercase keypress (blocks until key is pressed)."""
    b = msvcrt.getch()
    if b in (b"\x00", b"\xe0"):
        msvcrt.getch()   # consume second byte of extended key
        return None
    return b.decode("utf-8", errors="ignore").lower()


# ── Interactive mode ─────────────────────────────────────────────────────────

def _draw(cfg, saved_flash=False):
    """Render the full interactive config screen."""
    _clear()
    enable_ansi()
    accent  = get_accent(cfg)
    color_n = cfg.get("color", 1)
    enabled = cfg.get("enabled", True)

    print()
    print(f"  {accent}CoolTerminal v{VERSION}{RESET}  -  Configuration")
    print()
    print(f"  {accent}## Running CoolTerminal{RESET}    {BOLD}{str(enabled).lower()}{RESET}")
    print(f"  {accent}## Change color{RESET}            {BOLD}{color_n}{RESET}  ({COLOR_NAMES.get(color_n, '?')})")
    print()

    # Colour palette row
    print(f"  {DIM}Colors:{RESET}  ", end="")
    for n, name in COLOR_NAMES.items():
        code = COLOR_CODES[n]
        if n == color_n:
            print(f"{code}{BOLD}[{n}]{name}{RESET}  ", end="")
        else:
            print(f"{DIM}[{n}]{name}{RESET}  ", end="")
    print()
    print()

    if saved_flash:
        print(f"  {accent}Settings saved.{RESET}")
    else:
        print(f"  {BOLD}[1-7]{RESET} color   "
              f"{BOLD}[E]{RESET} toggle on/off   "
              f"{BOLD}[S]{RESET} save   "
              f"{BOLD}[X]{RESET} exit")

    print()
    print(f"  Key: ", end="", flush=True)


def interactive():
    """Full-screen interactive configuration loop."""
    cfg      = load_config()
    original = dict(cfg)

    while True:
        _draw(cfg)
        key = _getkey()
        if key is None:
            continue

        if key == "x":
            _clear()
            break

        elif key == "s":
            save_config(cfg)
            _draw(cfg, saved_flash=True)
            time.sleep(0.9)
            _clear()
            break

        elif key == "e":
            cfg["enabled"] = not cfg.get("enabled", True)

        elif key in "1234567":
            cfg["color"] = int(key)


# ── Direct (non-interactive) commands ────────────────────────────────────────

def _direct(args):
    """Handle terconfig <command> [value] calls."""
    cfg    = load_config()
    accent = get_accent(cfg)

    cmd = args[0].lower()

    if cmd in ("help", "--help", "-h"):
        print()
        print(f"  {accent}terconfig{RESET}              Interactive config  (S=save  X=exit)")
        print(f"  {accent}terconfig color <1-7>{RESET}  Set accent color")
        print(f"  {accent}terconfig enabled <bool>{RESET}  Enable / disable startup display")
        print(f"  {accent}terconfig reset{RESET}        Reset to defaults")
        print(f"  {accent}terconfig /exit{RESET}        Exit immediately")
        print()
        return

    if cmd in ("/exit", "exit"):
        sys.exit(0)

    if cmd == "color":
        if len(args) < 2:
            _err("Usage: terconfig color <1-7>")
            return
        try:
            n = int(args[1])
            assert 1 <= n <= 7
            cfg["color"] = n
            save_config(cfg)
            new_accent = get_accent(cfg)
            print(f"  {new_accent}## Change color{RESET}  ->  {BOLD}{n}{RESET}  ({COLOR_NAMES[n]})")
        except (ValueError, AssertionError):
            _err("Color must be a number between 1 and 7.")

    elif cmd == "enabled":
        if len(args) < 2:
            _err("Usage: terconfig enabled true|false")
            return
        val = args[1].lower()
        if val in ("true", "1", "yes", "on"):
            cfg["enabled"] = True
        elif val in ("false", "0", "no", "off"):
            cfg["enabled"] = False
        else:
            _err(f"Unknown value '{args[1]}'. Use true or false.")
            return
        save_config(cfg)
        print(f"  {accent}## Running CoolTerminal{RESET}  ->  {BOLD}{str(cfg['enabled']).lower()}{RESET}")

    elif cmd == "reset":
        save_config(DEFAULT_CONFIG.copy())
        print(f"  {accent}Reset to defaults.{RESET}")

    else:
        _err(f"Unknown command '{cmd}'.  Type 'terconfig help' for usage.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    enable_ansi()
    args = sys.argv[1:]

    if not args:
        interactive()
    else:
        _direct(args)


if __name__ == "__main__":
    main()
