# CoolTerminal

A lightweight Windows system-info display that runs automatically when you open
**PowerShell**, **CMD**, or **Windows Terminal** -- similar to `screenfetch` / `neofetch` on Linux.

```
  ██████████  ██████████     user@DESKTOP
  ██████████  ██████████     ---------------------
  ██████████  ██████████     OS:          Windows 11 Pro 25H2
  ██████████  ██████████     Build:       26200
                             Uptime:      3h 12m
  ██████████  ██████████     Shell:       PowerShell 5.1
  ██████████  ██████████     Resolution:  1920x1080
  ██████████  ██████████     CPU:         Intel Core i5-8500 @ 3.00GHz
  ██████████  ██████████     GPU:         Radeon Pro 560X
                             RAM:         14305MiB / 32646MiB
                             Disk:        655.2GiB / 883.4GiB (74%)
```

> [!WARNING]
> **Security Notice:** `Coolterminal.exe` has been manually tested and is **NOT** a virus. 
> 
> If your antivirus flags this file, it is a **false positive** caused by the device's heuristic scanner (common with unsigned Python executables).



---

## Install

**Option A -- EXE installer (no Python required on target machine)**

Run `dist\CoolTerminal-Setup.exe`. The installer:
- Deploys `coolterm.exe` and `terconfig.exe` to `%APPDATA%\CoolTerminal\bin\`
- Adds that directory to your user PATH
- Hooks into PowerShell profile and CMD AutoRun
- Prints "Install done." and closes

**Option B -- Python script**

```bat
python install.py
```

Requires Python 3.7+ on the machine. Installs the same way as the EXE installer.

Open a new terminal window after either option to see the display.

---

## Build the EXE installer

Run on the build machine (Python + pip required):

```bat
build.bat
```

Output:

```
dist\CoolTerminal-Setup.exe   -- self-contained installer (share this)
dist\coolterm.exe             -- standalone display tool
dist\terconfig.exe            -- config tool
```

Inno Setup 6 is optional. If installed, `build.bat` also produces
`Output\CoolTerminal-Installer.exe` (traditional Windows installer wizard).

---

## Commands

| Command | Description |
|---|---|
| `coolterm` | Display system info now |
| `coolterminal` | Same as coolterm |
| `terconfig` | Open interactive config |
| `terconfig color <1-7>` | Set accent color directly |
| `terconfig enabled true\|false` | Enable or disable startup display |
| `terconfig reset` | Reset to defaults |
| `terconfig /exit` | Exit immediately (no output) |
| `terconfig help` | Show command list |

---

## terconfig -- interactive mode

Type `terconfig` with no arguments to open the interactive config screen:

```
  CoolTerminal v1.0  -  Configuration

  ## Running CoolTerminal    true
  ## Change color            1  (Cyan)

  Colors:  [1]Cyan  [2]Green  [3]Red  [4]Yellow  [5]Magenta  [6]Blue  [7]White

  [1-7] color   [E] toggle on/off   [S] save   [X] exit

  Key: _
```

- Press **1-7** to change accent color (live preview)
- Press **E** to toggle display on/off
- Press **S** to save and exit
- Press **X** to exit without saving

---

## Requirements

- Windows 10 / 11
- Python 3.7+ (only for script mode / building from source)
- `psutil` (auto-installed by the Python installer; bundled in the EXE)

---

## Project structure

```
CoolTerminal/
├── coolterm_pkg/
│   ├── __init__.py
│   ├── config_manager.py   -- config read/write, color codes, ANSI setup
│   └── sysinfo.py          -- Windows system info (OS, CPU, GPU, RAM, Disk ...)
├── coolterm.py             -- display entry point
├── terconfig.py            -- interactive config tool
├── install.py              -- installer (Python script + PyInstaller bundle)
├── build.bat               -- build EXE installer
├── setup.iss               -- Inno Setup script (optional professional installer)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## License

[MIT](LICENSE) -- open source, free to use and modify.
