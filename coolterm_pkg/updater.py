"""
Update checker for CoolTerminal.
Fetches version.txt from the repo once per day.
If a newer version exists, prompts the user with Y/N.
"""

import os
import time
import urllib.request

LOCAL_VERSION  = "1.0.0"
VERSION_URL    = "https://raw.githubusercontent.com/nthung-bot/Coolterminal/main/version.txt"
DOWNLOAD_URL   = "https://github.com/nthung-bot/Coolterminal/releases/latest/download/CoolTerminal-Setup.exe"
CHECK_INTERVAL = 86400  # seconds — check at most once per 24 h


def _ver(v):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except Exception:
        return (0,)


def _fetch_remote(timeout=2):
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=timeout) as r:
            return r.read().decode().strip()
    except Exception:
        return None


def _download_and_run(accent, reset):
    import subprocess
    import tempfile

    print(f"  {accent}Downloading update...{reset}", flush=True)
    tmp = os.path.join(tempfile.gettempdir(), "CoolTerminal-Setup.exe")
    try:
        urllib.request.urlretrieve(DOWNLOAD_URL, tmp)
        # Plain string avoids Python subprocess quoting adding \"
        subprocess.Popen('cmd /c "' + tmp + '"', creationflags=0x00000010)
        print(f"  Installer launched in new window.")
    except Exception as exc:
        print(f"  Download failed: {exc}")
        print(f"  Get it at: https://github.com/nthung-bot/Coolterminal/releases")


def check_and_prompt(cfg, save_cfg, accent, reset, bold):
    """
    Called after the sysinfo display.
    Checks for a newer version at most once per day.
    If found, shows: There New Update From CoolTerminal! [Y] Install Update [N] Don't Install
    """
    # Skip if checked recently
    if time.time() - cfg.get("last_update_check", 0) < CHECK_INTERVAL:
        return

    # Record check time so we don't check again today
    cfg["last_update_check"] = time.time()
    save_cfg(cfg)

    remote = _fetch_remote()
    if remote is None or _ver(remote) <= _ver(LOCAL_VERSION):
        return

    # New version found — prompt
    import msvcrt
    print(
        f"\n  {accent}There New Update From CoolTerminal!{reset}  "
        f"{bold}[Y]{reset} Install Update  "
        f"{bold}[N]{reset} Don't Install  ",
        end="", flush=True,
    )

    key = msvcrt.getch().decode("utf-8", errors="ignore").lower()
    print()

    if key == "y":
        _download_and_run(accent, reset)
