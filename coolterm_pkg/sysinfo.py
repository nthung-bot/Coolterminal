import os
import platform
import socket
import subprocess
import ctypes


def _wmic(*args, timeout=6):
    """Run a wmic command and return stdout lines (non-header)."""
    try:
        result = subprocess.run(
            ["wmic"] + list(args),
            capture_output=True, text=True, timeout=timeout,
            creationflags=0x08000000,  # CREATE_NO_WINDOW
        )
        lines = [l.strip() for l in result.stdout.split("\n") if l.strip()]
        return lines[1:] if len(lines) > 1 else []
    except Exception:
        return []


def get_os_info():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
        )
        product = winreg.QueryValueEx(key, "ProductName")[0]
        try:
            disp = winreg.QueryValueEx(key, "DisplayVersion")[0]
        except OSError:
            disp = ""
        build = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
        winreg.CloseKey(key)

        # Windows 11 starts at build 22000; the registry ProductName may still
        # say "Windows 10" on some editions — correct it using the build number.
        if int(build) >= 22000 and "Windows 10" in product:
            product = product.replace("Windows 10", "Windows 11")

        return f"{product} {disp}".strip(), build
    except Exception:
        v = platform.version()
        build = v.split(".")[-1] if "." in v else v
        return f"Windows {platform.release()}", build


def get_uptime():
    try:
        ms = ctypes.windll.kernel32.GetTickCount64()
        s = ms // 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d:
            return f"{d}d {h}h {m}m"
        if h:
            return f"{h}h {m}m"
        return f"{m}m"
    except Exception:
        return "Unknown"


def get_cpu():
    lines = _wmic("cpu", "get", "name")
    if lines:
        return lines[0]
    return platform.processor() or "Unknown"


def get_gpu():
    lines = _wmic("path", "win32_VideoController", "get", "name")
    if lines:
        return ", ".join(lines)
    return "Unknown"


def get_ram():
    try:
        import psutil
        m = psutil.virtual_memory()
        used = m.used // (1024 * 1024)
        total = m.total // (1024 * 1024)
        return f"{used}MiB / {total}MiB"
    except ImportError:
        pass
    lines = _wmic("OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory")
    if lines:
        parts = lines[0].split()
        if len(parts) >= 2:
            free_kb = int(parts[0])
            total_kb = int(parts[1])
            used_kb = total_kb - free_kb
            return f"{used_kb // 1024}MiB / {total_kb // 1024}MiB"
    return "Unknown"


def get_disk():
    try:
        import psutil
        d = psutil.disk_usage("C:\\")
        used = d.used / (1024 ** 3)
        total = d.total / (1024 ** 3)
        return f"{used:.1f}GiB / {total:.1f}GiB ({d.percent:.0f}%)"
    except ImportError:
        pass
    lines = _wmic("logicaldisk", "where", 'DeviceID="C:"', "get", "Size,FreeSpace")
    if lines:
        parts = lines[0].split()
        if len(parts) >= 2:
            free = int(parts[0])
            size = int(parts[1])
            used = size - free
            pct = used / size * 100
            return f"{used/(1024**3):.1f}GiB / {size/(1024**3):.1f}GiB ({pct:.0f}%)"
    return "Unknown"


def get_shell():
    if os.environ.get("PSModulePath"):
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "$v=$PSVersionTable.PSVersion; \"$($v.Major).$($v.Minor)\""],
                capture_output=True, text=True, timeout=4,
                creationflags=0x08000000,
            )
            if r.returncode == 0 and r.stdout.strip():
                return f"PowerShell {r.stdout.strip()}"
        except Exception:
            pass
        return "PowerShell"
    return "cmd.exe"


def get_resolution():
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        return f"{w}x{h}"
    except Exception:
        return "Unknown"


def get_host_user():
    hostname = os.environ.get("COMPUTERNAME", socket.gethostname())
    username = os.environ.get("USERNAME", os.environ.get("USER", "user"))
    return hostname, username


def collect():
    os_name, build = get_os_info()
    hostname, username = get_host_user()
    return {
        "username": username,
        "hostname": hostname,
        "os":       os_name,
        "build":    build,
        "uptime":   get_uptime(),
        "shell":    get_shell(),
        "res":      get_resolution(),
        "cpu":      get_cpu(),
        "gpu":      get_gpu(),
        "ram":      get_ram(),
        "disk":     get_disk(),
    }
