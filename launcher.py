from i18n import tr, set_language
"""Visible startup errors even when launched using pythonw.exe."""
import ctypes
import os
from pathlib import Path
import sys
import traceback
from windows_settings import get_ui_language

set_language(get_ui_language())
sys.dont_write_bytecode = True


def report(kind, value, tb):
    data = Path(os.environ.get('DICTATOR_DATA_DIR', str(Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Diktatoro")))
    data.mkdir(parents=True, exist_ok=True)
    log = data / "startup-error.log"
    log.write_text("".join(traceback.format_exception(kind, value, tb)), encoding="utf-8")
    if '--self-test' in sys.argv:
        return
    ctypes.windll.user32.MessageBoxW(None,
        tr('Не удалось запустить Dictatoro 0.3.\n\n') + str(value) + tr('\n\nПодробности: ') + str(log),
        tr('Dictatoro 0.3 — ошибка'), 0x10)


sys.excepthook = report
try:
    from intel_runtime import load as load_intel_runtime
    load_intel_runtime()
    import app
    if '--self-test' in sys.argv:
        import onnxruntime, ctranslate2
        from PySide6.QtWidgets import QApplication
        test_app = QApplication([])
        if app.app_icon().isNull():
            raise RuntimeError('Application icon unavailable')
        from model_assets import bundled_base_path
        if bundled_base_path() is None:
            raise RuntimeError('Bundled Base model is missing or incomplete. Reinstall Dictatoro.')
    else:
        app.main()
except Exception:
    report(*sys.exc_info())
    sys.exit(1)
