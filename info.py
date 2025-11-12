from enum import Enum
import os
import platform
import subprocess
import gif_config
import platform

class OSName(Enum):
    WINDOWS = 1
    LINUX = 2

class Info(Enum):
    LINUX = 1
    KERNEL = 2
    DE = 3
    BASH = 4
    PHYS_MEM = 5

PLATFORM = OSName.LINUX if platform.system() == "Linux" else OSName.WINDOWS

def get_os_name():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.strip().split("=")[1].strip('"')
    except FileNotFoundError:
        return "Unknown"


def get_os_version():
    return platform.release()

def get_big_win_version():
    try:
        # Get full version string from PowerShell
        full_version = subprocess.check_output(
            ["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            text=True
        ).strip()

        return full_version
    except Exception as e:
        return f"Unknown ({e})"

def get_windows_feature_update():
    try:
        full_version = get_big_win_version()

        parts = full_version.split('.')
        major_minor = '.'.join(parts[2:4])
        return major_minor
    except Exception as e:
        return f"Unknown ({e})"

def get_desktop_environment():
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
    session = os.environ.get("XDG_SESSION_DESKTOP", "Unknown")
    window_manager = os.environ.get("XDG_SESSION_TYPE", "Unknown")

    return f"Session: {session}, WM: {window_manager}"


def get_bash_version():
    if PLATFORM == OSName.LINUX:
        try:
            result = subprocess.run(["bash", "--version"], capture_output=True, text=True)
            return result.stdout.split()[3]  # Get only the version number
        except FileNotFoundError:
            return "Bash not found"
    elif PLATFORM == OSName.WINDOWS:
        return platform.version().upper()



def get_powershell_major_minor():
    try:
        full_version = get_big_win_version()

        parts = full_version.split('.')
        major_minor = '.'.join(parts[:2])
        return major_minor
    except Exception as e:
        return f"Unknown ({e})"


def get_total_memory_proc():
    if PLATFORM == OSName.LINUX:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return f"{int(line.split()[1]) // 1024}M"  # Convert kB to MB
    elif PLATFORM == OSName.WINDOWS:
        output = subprocess.check_output(
            ["powershell", "-Command", "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"],
            text=True
        )

        total_bytes = int(output.strip())
        total_mb = int(total_bytes / (1024 ** 2))
        return f"{total_mb}M"


def get_system_info():
    if PLATFORM == OSName.WINDOWS:
        system_info = {
            Info.LINUX: f"Windows {platform.release()}",
            Info.KERNEL: get_windows_feature_update(),
            Info.DE: "Explorer",
            Info.BASH: get_powershell_major_minor(),
            Info.PHYS_MEM: get_total_memory_proc(),
        }
    elif PLATFORM == OSName.LINUX:
        system_info = {
            Info.LINUX: get_os_name(),
            Info.KERNEL: get_os_version(),
            Info.DE: get_desktop_environment(),
            Info.BASH: get_bash_version(),
            Info.PHYS_MEM: get_total_memory_proc(),
        }

    return system_info


def create_terminal_string(config: gif_config.Config, same_length=False):
    tab = config.TAB
    tab_length = config.TAB_LENGTH

    sys_info = get_system_info()
    terminal_string = ""

    tab_string = "" + (" " * tab_length) if tab else ""

    linux_string = f"{config.OVERRIDE_LINUX.upper() if len(config.OVERRIDE_LINUX) > 0 else sys_info.get(Info.LINUX).upper()}"
    kernel_string = f"{config.OVERRIDE_KERNEL.upper() if len(config.OVERRIDE_KERNEL) > 0 else sys_info.get(Info.KERNEL).upper()}"
    de_string = f"{config.OVERRIDE_DE.upper() if len(config.OVERRIDE_DE) > 0 else sys_info.get(Info.DE).upper()}"
    bash_string = f"{config.OVERRIDE_BASH.upper() if len(config.OVERRIDE_BASH) > 0 else sys_info.get(Info.BASH).upper()}"
    mem_string = f"{config.OVERRIDE_PHYS_MEM.upper() if len(config.OVERRIDE_PHYS_MEM) > 0 else sys_info.get(Info.PHYS_MEM).upper()}"

    lines = [
        f"******** {linux_string} ********",
        "",
        f"{tab_string}COPYRIGHT 2075 ROBCO(R)",
        f"{tab_string}KERNEL {kernel_string}",
        f"{tab_string}BASH VERSION {bash_string}",
        f"{tab_string}{mem_string} RAM SYSTEM",
        f"{tab_string}{de_string}",
        f"{tab_string}NO HOLOTAPE FOUND",
        f"{tab_string}LOAD ROM(1): DEITRIX 303",
        "",
        ""
    ]

    if same_length:
        max_length = max(len(line) for line in lines)
        padded_lines = [line.ljust(max_length) for line in lines]

        terminal_string = "\n".join(padded_lines)
    else:
        terminal_string = "\n".join(lines)

    return terminal_string
