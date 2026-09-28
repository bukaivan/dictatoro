"""Windows low-level mouse hook. Only the selected button is consumed."""
import ctypes
from ctypes import wintypes as wt
import threading


def button_event(message, mouse_data=0):
    if message in (0x207, 0x208):
        return "middle", message == 0x207
    if message in (0x20B, 0x20C):
        button = (mouse_data >> 16) & 0xFFFF
        if button in (1, 2):
            return ("x1" if button == 1 else "x2"), message == 0x20B
    return None


class MouseHook:
    def __init__(self, button, callback):
        if button not in ("middle", "x1", "x2"):
            raise ValueError("Unsupported mouse button")
        self.button, self.callback = button, callback
        self.ready = threading.Event()
        self.error = None
        self.thread_id = None
        self.thread = None
        self.stopped = False

    def start(self):
        self.thread = threading.Thread(target=self.run, name="DictatorMouse", daemon=True)
        self.thread.start()
        if not self.ready.wait(5):
            self.stop()
            raise RuntimeError("Mouse hook startup timed out")
        if self.error:
            raise self.error
        return self

    def stop(self):
        self.stopped = True
        if self.thread_id is not None:
            ctypes.windll.user32.PostThreadMessageW(self.thread_id, 0x12, 0, 0)
        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(2)

    def dispatch(self, message, mouse_data=0, flags=0):
        if flags & 1 or self.stopped:
            return False  # Injected events are never captured.
        event = button_event(message, mouse_data)
        if event and event[0] == self.button:
            self.callback(event[1])
            return True
        return False

    def run(self):
        user = ctypes.WinDLL("user32", use_last_error=True)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        result_type = ctypes.c_ssize_t
        proc_type = ctypes.WINFUNCTYPE(result_type, ctypes.c_int, wt.WPARAM, wt.LPARAM)
        class MouseData(ctypes.Structure):
            _fields_ = [("pt", wt.POINT), ("mouseData", wt.DWORD), ("flags", wt.DWORD),
                        ("time", wt.DWORD), ("extra", ctypes.c_size_t)]
        user.SetWindowsHookExW.argtypes = [ctypes.c_int, proc_type, wt.HINSTANCE, wt.DWORD]
        user.SetWindowsHookExW.restype = wt.HANDLE
        user.CallNextHookEx.argtypes = [wt.HANDLE, ctypes.c_int, wt.WPARAM, wt.LPARAM]
        user.CallNextHookEx.restype = result_type
        user.UnhookWindowsHookEx.argtypes = [wt.HANDLE]
        user.GetMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT]
        user.PeekMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT, wt.UINT]
        kernel.GetModuleHandleW.argtypes = [wt.LPCWSTR]
        kernel.GetModuleHandleW.restype = wt.HMODULE
        hook = None
        def procedure(code, message, address):
            if code >= 0 and message in (0x207, 0x208, 0x20B, 0x20C):
                data = ctypes.cast(address, ctypes.POINTER(MouseData)).contents
                try:
                    if self.dispatch(message, data.mouseData, data.flags):
                        return 1
                except Exception:
                    pass  # Never break the system's hook chain on an application error.
            return user.CallNextHookEx(None, code, message, address)
        self._procedure = proc_type(procedure)
        try:
            self.thread_id = kernel.GetCurrentThreadId()
            message = wt.MSG()
            user.PeekMessageW(ctypes.byref(message), None, 0, 0, 0)
            hook = user.SetWindowsHookExW(14, self._procedure, kernel.GetModuleHandleW(None), 0)
            if not hook:
                raise ctypes.WinError(ctypes.get_last_error())
            self.ready.set()
            while not self.stopped:
                result = user.GetMessageW(ctypes.byref(message), None, 0, 0)
                if result <= 0:
                    break
                user.TranslateMessage(ctypes.byref(message))
                user.DispatchMessageW(ctypes.byref(message))
        except Exception as exc:
            self.error = exc
            self.ready.set()
        finally:
            if hook:
                user.UnhookWindowsHookEx(hook)
            self.thread_id = None
