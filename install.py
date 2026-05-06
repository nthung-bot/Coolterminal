#!/usr/bin/env python3
"""
CoolTerminal Installer
======================
Two modes:
  • Frozen EXE  (CoolTerminal-Setup.exe) — deploys bundled coolterm.exe /
    terconfig.exe.  No Python required on the target machine.
  • Script      (python install.py)      — deploys .py files + .bat wrappers.
    Python 3.7+ must already be installed.

MIT License - https://github.com/NguyenTanHung/CoolTerminal
"""

import ctypes
import json
import os
import shutil
import subprocess
import sys
import winreg

VERSION     = "1.0.0"
APPDATA     = os.environ.get("APPDATA", os.path.expanduser("~"))
INSTALL_DIR = os.path.join(APPDATA, "CoolTerminal")
BIN_DIR     = os.path.join(INSTALL_DIR, "bin")
CONFIG_DIR  = INSTALL_DIR
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

IS_FROZEN = getattr(sys, "frozen", False)

# ANSI colour helpers
_R = "\033[0m"
_C = "\033[96m"
_G = "\033[92m"
_Y = "\033[93m"
_E = "\033[91m"
_B = "\033[1m"


# ── Console setup ────────────────────────────────────────────────────────────

def _ansi():
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass
    try:
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-11)
        m = ctypes.c_ulong()
        k.GetConsoleMode(h, ctypes.byref(m))
        k.SetConsoleMode(h, m.value | 0x0004)
    except Exception:
        pass
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _ok(msg):   print(f"  {_G}✓{_R}  {msg}")
def _warn(msg): print(f"  {_Y}⚠{_R}  {msg}")
def _fail(msg): print(f"  {_E}✗{_R}  {msg}")
def _info(msg): print(f"  {_C}→{_R}  {msg}")


def _header():
    mode = "EXE" if IS_FROZEN else "Script"
    print()
    print(f"  {_C}╔══════════════════════════════════════╗{_R}")
    print(f"  {_C}║   CoolTerminal v{VERSION}  Installer     ║{_R}")
    print(f"  {_C}╚══════════════════════════════════════╝{_R}")
    print()
    _info(f"Mode: {mode}  |  Target: {INSTALL_DIR}")
    print()


# ── Python discovery (script mode only) ──────────────────────────────────────

def _find_python():
    """Return path to a working Python 3 executable."""
    for candidate in ("py", "python", "python3"):
        path = shutil.which(candidate)
        if not path:
            continue
        try:
            r = subprocess.run(
                [path, "--version"], capture_output=True, text=True, timeout=5
            )
            out = r.stdout + r.stderr
            if "Python 3" in out:
                return path
        except Exception:
            pass
    # Fallback: common installation locations
    localappdata = os.environ.get("LOCALAPPDATA", "")
    for pattern in [
        os.path.join(localappdata, "Python", "bin", "python.exe"),
        os.path.join(localappdata, "Programs", "Python", "Python3*", "python.exe"),
    ]:
        import glob
        for m in sorted(glob.glob(pattern)):
            return m
    raise RuntimeError(
        "Python 3 not found. Install Python from https://python.org and re-run."
    )


# ── Deployment ────────────────────────────────────────────────────────────────

def _deploy_frozen():
    """
    EXE mode: extract coolterm.exe and terconfig.exe from the bundle and copy
    them to BIN_DIR.  No Python is needed on the target machine.
    """
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)

    meipass = sys._MEIPASS
    for exe in ("coolterm.exe", "terconfig.exe"):
        src = os.path.join(meipass, exe)
        if not os.path.exists(src):
            _fail(f"{exe} not found in bundle — rebuild with build.bat")
            sys.exit(1)
        shutil.copy2(src, os.path.join(BIN_DIR, exe))

    # coolterminal alias  →  calls coolterm.exe (simple, no AutoRun guard
    # needed because EXE does not spawn cmd.exe)
    with open(os.path.join(BIN_DIR, "coolterminal.bat"), "w") as f:
        f.write(f'@echo off\n"{os.path.join(BIN_DIR, "coolterm.exe")}"\n')

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"enabled": True, "color": 1}, f, indent=4)

    _ok(f"Deployed executables → {BIN_DIR}")
    return (
        os.path.join(BIN_DIR, "coolterm.exe"),
        os.path.join(BIN_DIR, "terconfig.exe"),
    )


def _deploy_script():
    """
    Script mode: copy .py source files and create .bat wrappers.
    Uses COOLTERM_ACTIVE guard in coolterm.bat to prevent double-display
    when PowerShell's & operator spawns cmd.exe which fires both AutoRun
    and the /c argument.
    """
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)

    src_root = os.path.dirname(os.path.abspath(__file__))

    pkg_src = os.path.join(src_root, "coolterm_pkg")
    pkg_dst = os.path.join(INSTALL_DIR, "coolterm_pkg")
    if os.path.exists(pkg_dst):
        shutil.rmtree(pkg_dst)
    shutil.copytree(pkg_src, pkg_dst)

    for name in ("coolterm.py", "terconfig.py"):
        shutil.copy2(os.path.join(src_root, name), os.path.join(INSTALL_DIR, name))

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump({"enabled": True, "color": 1}, f, indent=4)

    _ok(f"Copied source files → {INSTALL_DIR}")

    python_exe = _find_python()
    _ok(f"Python: {python_exe}")

    coolterm_bat    = os.path.join(BIN_DIR, "coolterm.bat")
    coolterminal_bat = os.path.join(BIN_DIR, "coolterminal.bat")
    terconfig_bat   = os.path.join(BIN_DIR, "terconfig.bat")
    coolterm_py     = os.path.join(INSTALL_DIR, "coolterm.py")
    terconfig_py    = os.path.join(INSTALL_DIR, "terconfig.py")

    guard = (
        "@echo off\n"
        "if defined COOLTERM_ACTIVE exit /b 0\n"
        "set COOLTERM_ACTIVE=1\n"
    )

    with open(coolterm_bat, "w") as f:
        f.write(guard + f'"{python_exe}" "{coolterm_py}"\n')

    with open(coolterminal_bat, "w") as f:
        f.write(guard + f'"{python_exe}" "{coolterm_py}"\n')

    with open(terconfig_bat, "w") as f:
        f.write(f'@echo off\n"{python_exe}" "{terconfig_py}" %*\n')

    _ok("Created coolterm, coolterminal, and terconfig commands")
    return coolterm_bat, terconfig_bat


# ── PATH ─────────────────────────────────────────────────────────────────────

def _add_to_path():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment",
            0, winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            current, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current = ""

        paths = [p for p in current.split(";") if p]
        if BIN_DIR.lower() not in [p.lower() for p in paths]:
            paths.append(BIN_DIR)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, ";".join(paths))
            _ok("Added to user PATH")
        else:
            _ok("Already in PATH")
        winreg.CloseKey(key)

        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 2, 5000, None
        )
    except Exception as exc:
        _warn(f"Could not update PATH: {exc}")
        _warn(f"Add manually: {BIN_DIR}")


# ── Shell hooks ───────────────────────────────────────────────────────────────

def _setup_powershell(coolterm_path):
    """
    Add CoolTerminal to the PowerShell profile.

    When running in EXE mode we call the .exe directly from PowerShell's &
    operator — no cmd.exe is spawned, so CMD AutoRun never fires and there is
    no double-display.  In script mode the .bat wrapper is called; the
    COOLTERM_ACTIVE guard in the bat prevents the double-display.
    """
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "$PROFILE"],
            capture_output=True, text=True, timeout=6,
        )
        profile_path = r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        profile_path = None

    if not profile_path:
        profile_path = os.path.join(
            os.path.expanduser("~"), "Documents",
            "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1",
        )

    marker = "# CoolTerminal-autorun"
    # Escape backslashes for the PS string literal
    ct_ps = coolterm_path.replace("\\", "\\\\")
    entry = (
        f"\n{marker}\n"
        f'if (Test-Path "{ct_ps}") {{ & "{ct_ps}" }}\n'
    )

    os.makedirs(os.path.dirname(profile_path), exist_ok=True)

    if os.path.exists(profile_path):
        content = open(profile_path).read()
        if marker in content:
            _ok("PowerShell profile already configured")
            return

    with open(profile_path, "a") as f:
        f.write(entry)
    _ok(f"PowerShell profile updated")


def _setup_cmd_autorun(coolterm_path):
    """Set CMD AutoRun to run CoolTerminal when a CMD window opens."""
    try:
        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Command Processor",
            0, winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            current, _ = winreg.QueryValueEx(key, "AutoRun")
        except FileNotFoundError:
            current = ""

        entry = f'"{coolterm_path}"'
        if coolterm_path.lower() not in current.lower():
            new_val = f"{current} & {entry}" if current.strip() else entry
            winreg.SetValueEx(key, "AutoRun", 0, winreg.REG_SZ, new_val)
            _ok("CMD AutoRun configured")
        else:
            _ok("CMD AutoRun already configured")
        winreg.CloseKey(key)
    except Exception as exc:
        _warn(f"Could not configure CMD AutoRun: {exc}")


# ── Finish ────────────────────────────────────────────────────────────────────

def _footer():
    print()
    print(f"  {_G}Install done.{_R}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    _ansi()
    _header()

    if IS_FROZEN:
        # ── EXE mode ─────────────────────────────────────────────────────────
        coolterm_path, _terconfig_path = _deploy_frozen()
        _add_to_path()
        _setup_powershell(coolterm_path)
        _setup_cmd_autorun(coolterm_path)
    else:
        # ── Script mode ───────────────────────────────────────────────────────
        _ok(f"Python {sys.version.split()[0]}")
        try:
            import psutil  # noqa: F401
            _ok("psutil already installed")
        except ImportError:
            _info("Installing psutil...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "psutil", "--quiet"],
                    check=True,
                )
                _ok("psutil installed")
            except subprocess.CalledProcessError:
                _warn("psutil install failed — some info may use fallback values.")

        coolterm_path, _terconfig_path = _deploy_script()
        _add_to_path()
        _setup_powershell(coolterm_path)
        _setup_cmd_autorun(coolterm_path)

    _footer()


if __name__ == "__main__":
    main()
