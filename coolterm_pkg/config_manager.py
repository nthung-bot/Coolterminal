import json
import os

APPDATA = os.environ.get("APPDATA", os.path.expanduser("~"))
CONFIG_DIR = os.path.join(APPDATA, "CoolTerminal")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "enabled": True,
    "color": 1,
}

# ANSI color codes mapped by number (1-7)
COLOR_CODES = {
    1: "\033[96m",   # Bright Cyan
    2: "\033[92m",   # Bright Green
    3: "\033[91m",   # Bright Red
    4: "\033[93m",   # Bright Yellow
    5: "\033[95m",   # Bright Magenta
    6: "\033[94m",   # Bright Blue
    7: "\033[97m",   # Bright White
}

COLOR_NAMES = {
    1: "Cyan",
    2: "Green",
    3: "Red",
    4: "Yellow",
    5: "Magenta",
    6: "Blue",
    7: "White",
}

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)


def get_accent(cfg=None):
    if cfg is None:
        cfg = load_config()
    num = cfg.get("color", 1)
    return COLOR_CODES.get(num, COLOR_CODES[1])


def enable_ansi():
    """Enable VT100 (ANSI) and UTF-8 output on Windows 10+."""
    import sys
    import ctypes

    # Switch console to UTF-8 (code page 65001) so block chars render
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

    # Enable VIRTUAL_TERMINAL_PROCESSING for ANSI escape codes
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass

    # Reconfigure stdout to UTF-8 so Python encodes block chars correctly
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
