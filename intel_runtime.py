"""Load the separately installed Intel runtime using Windows Installer metadata."""
import ctypes
from ctypes import wintypes
from pathlib import Path
import os

PRODUCT = '{0C8A072B-5439-4421-B569-0AB7D14F0005}'
COMPONENT = '{CC95C88A-4143-4039-B3D2-AB68D333B651}'
_handles = []


def installed_path():
    msi = ctypes.WinDLL('msi')
    get_path = msi.MsiGetComponentPathW
    get_path.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPWSTR,
                         ctypes.POINTER(wintypes.DWORD)]
    get_path.restype = ctypes.c_int
    size = wintypes.DWORD(32768)
    buffer = ctypes.create_unicode_buffer(size.value)
    state = get_path(PRODUCT, COMPONENT, buffer, ctypes.byref(size))
    if state != 3 or not Path(buffer.value).is_file():
        raise RuntimeError('Intel runtime is missing. Run the Dictatoro installer again to install Intel runtime.')
    return Path(buffer.value)


def load():
    # Older development runtimes still carry their own DLL. The external-runtime
    # installer omits it and removes that exact obsolete file during upgrades.
    local = Path(__file__).parent / 'runtime/Lib/site-packages/ctranslate2/libiomp5md.dll'
    if local.is_file():
        return
    path = installed_path()
    _handles.append(os.add_dll_directory(str(path.parent)))
    _handles.append(ctypes.CDLL(str(path)))
