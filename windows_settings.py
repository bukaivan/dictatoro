"""Per-user Windows preferences; no administrator privileges needed."""
from pathlib import Path
import subprocess
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_KEY = r"Software\Dictator"


def startup_command(folder):
    return subprocess.list2cmdline([str(Path(folder).resolve() / 'Dictator.exe'), '--startup'])


def autostart_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, 'Dictator')
            return bool(value)
    except FileNotFoundError:
        return False


def set_autostart(enabled, folder):
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            launcher = Path(folder) / 'Dictator.exe'
            if not launcher.is_file():
                raise FileNotFoundError('Dictator.exe')
            winreg.SetValueEx(key, 'Dictator', 0, winreg.REG_SZ, startup_command(folder))
        else:
            try:
                winreg.DeleteValue(key, 'Dictator')
            except FileNotFoundError:
                pass


def get_ui_language(fallback='ru'):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, APP_KEY) as key:
            value, _ = winreg.QueryValueEx(key, 'UILanguage')
            return value if value in ('ru', 'en', 'pl', 'es', 'de', 'fr', 'ar', 'zh') else fallback
    except FileNotFoundError:
        return fallback


def set_ui_language(value):
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, APP_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, 'UILanguage', 0, winreg.REG_SZ, value)
