"""Dictator — Windows push-to-talk, entirely local inference."""
import ctypes
from ctypes import wintypes
import json
import logging
import os
from pathlib import Path
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import keyboard
import numpy as np
import sounddevice as sd
import win32clipboard
import win32con
import win32gui
import win32process
from faster_whisper import WhisperModel
from PySide6 import QtCore, QtGui, QtWidgets
from core import DEFAULTS, KEYS, MODELS, LANGUAGES, UI_LANGUAGES, MOUSE_BUTTONS, validate_config, can_insert, key_label, matches_custom
from key_picker import KeyPicker
from icon_art import app_icon
from mouse_hook import MouseHook
from windows_settings import autostart_enabled, set_autostart, get_ui_language, set_ui_language
from i18n import tr, set_language
from modern_ui import build_ui, STYLE, update_hints
from audio_processing import resample_microphone
from model_assets import bundled_base_path

DATA = Path(os.environ.get('DICTATOR_DATA_DIR', str(Path(os.environ["LOCALAPPDATA"]) / "Diktatoro")))
DATA.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=DATA / "app.log", level=logging.WARNING,
                    format="%(asctime)s %(levelname)s %(message)s")


class Events(QtCore.QObject):
    key = QtCore.Signal(bool)
    loaded = QtCore.Signal(object, str)
    result = QtCore.Signal(str, str, object)


def process_of(hwnd):
    try:
        return win32process.GetWindowThreadProcessId(hwnd)[1]
    except Exception:
        return 0


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(app_icon())
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setFixedSize(680, 500)
        try:
            self.config = validate_config(json.loads((DATA / "settings.json").read_text("utf-8")))
        except (OSError, ValueError, TypeError, AttributeError):
            self.config = dict(DEFAULTS)
        self.config['ui_language'] = get_ui_language(self.config['ui_language'])
        set_language(self.config['ui_language'])
        self.display_language = self.config['ui_language']
        self.setWindowTitle('Dictatoro 0.3')
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.events = Events()
        self.events.key.connect(self.handle_key)
        self.events.loaded.connect(self.on_loaded)
        self.events.result.connect(self.on_result)
        self.model = None
        self.ready_model_name = None
        self.record_source = None
        self.ui_building = False
        self.busy = False
        self.pressed = False
        self.stream = None
        self.chunks = []
        self.hooks = []
        self.mouse_hook = None
        self.target = 0
        self.target_pid = 0
        self.closing = False
        self.audio_error = False
        self.picking = False
        build_ui(self)
        self.tray = QtWidgets.QSystemTrayIcon(self.make_icon("#74baff"), self)
        self.tray.setToolTip("Dictatoro")
        self.build_tray_menu()
        self.tray.activated.connect(lambda reason: self.open_window()
            if reason == QtWidgets.QSystemTrayIcon.DoubleClick else None)
        self.tray.show()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(80)
        QtCore.QTimer.singleShot(100, lambda: self.load_model(True))

    def build_tray_menu(self):
        old = getattr(self, 'tray_menu', None)
        self.tray_menu = QtWidgets.QMenu(self)
        self.tray_menu.addAction(tr('Главная'), lambda: self.open_page(0))
        self.tray_menu.addAction(tr('Настройки'), lambda: self.open_page(1))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(tr('Выход'), self.quit_app)
        self.tray.setContextMenu(self.tray_menu)
        if old is not None:
            old.deleteLater()

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        for n, button in enumerate(self.nav_buttons):
            button.setChecked(n == index)

    def open_page(self, index):
        self.navigate(index)
        self.open_window()

    def populate_microphones(self):
        try:
            for device in sd.query_devices():
                if device['max_input_channels'] > 0 and self.device_box.findData(device['name']) < 0:
                    self.device_box.addItem(device['name'], device['name'])
            self.device_box.setCurrentIndex(max(0, self.device_box.findData(self.config['device'])))
        except Exception:
            logging.exception('Device enumeration failed')

    @staticmethod
    def read_autostart():
        try:
            return autostart_enabled()
        except OSError:
            return False

    def persist(self):
        temp = DATA / 'settings.tmp'
        temp.write_text(json.dumps(self.config, ensure_ascii=False), encoding='utf-8')
        temp.replace(DATA / 'settings.json')

    def on_preferences_changed(self, *_):
        if self.ui_building or self.picking or self.busy or self.stream is not None:
            return
        previous = dict(self.config)
        self.config.update(key=self.key_box.currentData(), model=self.model_box.currentText(),
            language=self.lang_box.currentData(), device=self.device_box.currentData(),
            translate_to_english=self.translation_box.isChecked())
        try:
            self.persist()
            update_hints(self)
            if previous['model'] != self.config['model']:
                self.model = None
                self.ready_model_name = None
                self.unhook()
                self.load_model(True)
            elif self.model is not None:
                self.bind()
                self.set_status(tr('Сохранено. Удерживайте ') + self.trigger_label() + tr(' и говорите.'))
            else:
                self.set_status(tr('Кнопка сохранена. Загрузите модель, чтобы начать.'))
        except Exception as exc:
            self.config = previous
            blocker = QtCore.QSignalBlocker(self.translation_box)
            self.translation_box.setChecked(previous['translate_to_english'])
            del blocker
            model_blocker = QtCore.QSignalBlocker(self.model_box)
            self.model_box.select(previous['model'])
            del model_blocker
            update_hints(self)
            self.set_status(tr('Не удалось сохранить настройки: ') + str(exc))

    def change_language(self, *_):
        if self.ui_building or self.busy or self.stream is not None:
            return
        language = self.ui_language_box.currentData()
        previous = self.config['ui_language']
        persisted = False
        try:
            self.config['ui_language'] = language
            self.persist()
            persisted = True
            set_ui_language(language)
            set_language(language)
            self.display_language = language
            result, index = self.text.toPlainText(), self.pages.currentIndex()
            build_ui(self, result, index)
            self.build_tray_menu()
            if self.model is not None:
                self.set_status(tr('Готово. Удерживайте ') + self.trigger_label() + tr(' и говорите.'))
            self.settings_status.setText(tr('Изменения сохранены'))
        except Exception as exc:
            self.config['ui_language'] = previous
            if persisted:
                try:
                    self.persist()
                    set_ui_language(previous)
                except Exception:
                    logging.exception('Could not restore language preferences')
            set_language(previous)
            self.display_language = previous
            blocker = QtCore.QSignalBlocker(self.ui_language_box)
            self.ui_language_box.setCurrentIndex(self.ui_language_box.findData(previous))
            del blocker
            self.settings_status.setText(tr('Не удалось сохранить настройки: ') + str(exc))

    def toggle_recording(self):
        if self.stream is not None:
            self.stop_recording()
        elif self.model is not None and not self.busy:
            self.start_recording(manual=True)

    @staticmethod
    def make_icon(color):
        return app_icon(color)

    def open_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def set_status(self, message, color="#74baff"):
        self.status.setText(message)
        self.tray.setToolTip("Dictatoro: " + message[:100])
        self.tray.setIcon(self.make_icon(color))

    def unhook(self):
        if self.mouse_hook is not None:
            self.mouse_hook.stop()
            self.mouse_hook = None
        for hook in self.hooks:
            keyboard.unhook(hook)
        self.hooks = []

    def bind(self):
        self.unhook()
        self.pressed = False
        key = self.config["key"]
        if isinstance(key, dict) and 'mouse' in key:
            self.mouse_hook = MouseHook(key['mouse'], self.events.key.emit).start()
            return
        scan_codes = keyboard.key_to_scan_codes(key) if isinstance(key, str) else None
        # Hook callback never touches Qt widgets or waits for inference.
        def on_key(event):
            if isinstance(key, dict):
                matched = matches_custom(key, event)
            else:
                matched = event.scan_code in scan_codes
                if key.startswith(("right ", "left ")):
                    matched = matched and event.name == key
            if not matched:
                return True
            self.events.key.emit(event.event_type == "down")
            return False
        self.hooks.append(keyboard.hook(on_key, suppress=True))

    def trigger_label(self):
        key = self.config['key']
        return self.mouse_names[key['mouse']] if isinstance(key, dict) and 'mouse' in key else key_label(key)

    def change_autostart(self, enabled):
        try:
            set_autostart(enabled, Path(__file__).resolve().parent)
            self.settings_status.setText(tr('Автозапуск включён.') if enabled else tr('Автозапуск выключен.'))
        except Exception as exc:
            self.startup_box.blockSignals(True)
            self.startup_box.setChecked(not enabled)
            self.startup_box.blockSignals(False)
            self.settings_status.setText(tr('Не удалось изменить автозапуск: ') + str(exc))

    def choose_key(self):
        if self.busy or self.stream is not None:
            return
        selection = None
        self.picking = True
        self.unhook()
        try:
            picker = KeyPicker(self)
            try:
                selection = picker.choose()
            finally:
                picker.deleteLater()
            if selection is not None:
                selection = validate_config({'key': selection})['key']
                index = self.key_box.findData(selection)
                if index < 0:
                    self.key_box.addItem(key_label(selection), selection)
                    index = self.key_box.count() - 1
                self.key_box.setCurrentIndex(index)
        except Exception as exc:
            self.set_status(tr('Не удалось выбрать клавишу: ') + str(exc))
        finally:
            self.picking = False
            if selection is not None:
                self.on_preferences_changed()
            elif self.model is not None:
                self.bind()

    def apply(self):
        if self.busy or self.stream is not None:
            return
        self.on_preferences_changed()
        if self.model is None:
            self.load_model(False)

    def load_model(self, offline):
        self.busy = True
        self.loading_model = True
        self.apply_button.setEnabled(False)
        self.unhook()
        self.model = None
        self.set_status(tr('Проверка локальной модели…') if offline else tr('Загрузка модели… Это может занять несколько минут.'))
        name = self.config["model"]
        bundled = bundled_base_path() if name == 'base' else None
        def work():
            try:
                model = WhisperModel(str(bundled) if bundled else name, device="cpu", compute_type="int8",
                    download_root=str(DATA / "models"), local_files_only=True if bundled else offline)
                self.events.loaded.emit(model, "")
            except Exception as exc:
                logging.exception("Model loading failed")
                self.events.loaded.emit(None, (tr('Не удалось открыть встроенную модель Base. Переустановите Dictatoro.') + ' ' + str(exc)) if bundled else tr('Загрузите модель, чтобы начать') if offline
                    else tr('Ошибка загрузки: ') + str(exc))
        self.pool.submit(work)

    def on_loaded(self, model, error):
        self.busy = False
        self.loading_model = False
        self.apply_button.setEnabled(True)
        self.model = model
        self.ready_model_name = self.config["model"] if model is not None else None
        if error:
            self.set_status(error)
        else:
            try:
                self.bind()
                self.set_status(tr('Готово. Удерживайте ') + self.trigger_label() + tr(' и говорите.'))
            except Exception as exc:
                self.set_status(tr('Не удалось назначить клавишу: ') + str(exc))

    def handle_key(self, down):
        if self.picking:
            return
        if down == self.pressed:
            return
        self.pressed = down
        if down:
            if self.busy or self.model is None or self.closing:
                return
            if self.stream is None:
                self.start_recording()
        elif self.stream is not None and self.record_source == "hotkey":
            self.stop_recording()

    def start_recording(self, manual=False):
        if self.stream is not None or self.busy or self.model is None:
            return
        self.record_source = "manual" if manual else "hotkey"
        self.target = 0 if manual else win32gui.GetForegroundWindow()
        self.target_pid = process_of(self.target)
        self.chunks = []
        self.audio_error = False
        self.level = 0
        try:
            device = self.config["device"]
            self.rate = int(sd.query_devices(device, "input")["default_samplerate"])
            def audio_callback(data, frames, timing, status):
                if status:
                    self.audio_error = True
                self.chunks.append(data.copy())
                self.level = min(100, int(float(np.sqrt(np.mean(data * data))) * 500))
            self.stream = sd.InputStream(device=device, samplerate=self.rate, channels=1,
                dtype="float32", callback=audio_callback)
            self.started = time.monotonic()
            self.stream.start()
            self.apply_button.setEnabled(False)
            self.set_status(tr('● Запись… Отпустите кнопку для вставки текста.'), "#fb7185")
        except Exception as exc:
            if self.stream is not None:
                try:
                    self.stream.close()
                except Exception:
                    logging.exception('Microphone cleanup failed after startup error')
            self.stream = None
            self.set_status(tr('Ошибка микрофона: ') + str(exc))

    def tick(self):
        idle = not self.busy and self.stream is None
        for widget in (self.custom_button, self.key_box, self.model_box, self.lang_box, self.device_box, self.ui_language_box, self.translation_box):
            widget.setEnabled(idle)
        recording = self.stream is not None
        self.record_button.setEnabled(recording or (self.model is not None and not self.busy))
        self.record_button.setText(tr('Остановить запись') if recording else tr('Начать запись'))
        if self.record_button.property('recording') != recording:
            self.record_button.setProperty('recording', recording)
            self.record_button.style().unpolish(self.record_button)
            self.record_button.style().polish(self.record_button)
        self.apply_button.setEnabled(idle and self.model is None)
        self.apply_button.setText(tr('Подготовка модели…') if getattr(self, 'loading_model', False)
            else tr('Модель готова') if self.model is not None else tr('Загрузить модель'))
        if self.stream is not None:
            self.meter.setValue(self.level)
            if time.monotonic() - self.started >= 120:
                self.stop_recording()

    def stop_recording(self):
        stream, self.stream = self.stream, None
        if stream is None:
            return
        try:
            stream.stop()
        except Exception:
            self.audio_error = True
            logging.exception('Microphone failed while stopping; keeping captured audio')
        finally:
            try:
                stream.close()
            except Exception:
                self.audio_error = True
                logging.exception('Microphone failed while closing')
        self.meter.setValue(0)
        chunks, self.chunks = self.chunks, []
        if not chunks or sum(len(x) for x in chunks) < self.rate * 0.25:
            self.apply_button.setEnabled(True)
            self.set_status(tr('Слишком короткая запись. Удерживайте клавишу и говорите.'))
            return
        self.busy = True
        self.set_status(tr('Распознавание на компьютере…'), "#fbbf24")
        target = (self.target, self.target_pid)
        rate = self.rate
        language = None if self.config["language"] == "auto" else self.config["language"]
        task = "translate" if self.config["translate_to_english"] else "transcribe"
        audio_error = self.audio_error
        vocabulary = self.config.get('vocabulary', '').replace('\n', ', ')
        def work():
            try:
                samples = np.concatenate(chunks).reshape(-1)
                samples = resample_microphone(samples, rate)
                segments, _ = self.model.transcribe(samples, language=language, task=task, vad_filter=True,
                    beam_size=5, condition_on_previous_text=False,
                    hotwords=vocabulary if task == 'transcribe' and vocabulary else None)
                result = " ".join(s.text.strip() for s in segments).strip()
                self.events.result.emit(result, tr('В записи были пропуски звука; проверьте текст.') if audio_error else "", target)
            except Exception as exc:
                logging.exception("Transcription failed")
                self.events.result.emit("", tr('Ошибка распознавания: ') + str(exc), target)
        self.pool.submit(work)

    def on_result(self, text, error, target):
        self.busy = False
        self.apply_button.setEnabled(True)
        if not text:
            self.set_status(error or tr('Речь не обнаружена. Попробуйте говорить ближе к микрофону.'))
            return
        self.text.setPlainText(text)
        hwnd, pid = target
        if not hwnd:
            self.set_status(error or tr('Текст готов. Его можно скопировать.'))
            return
        current = win32gui.GetForegroundWindow()
        if not can_insert(hwnd, current, os.getpid(), process_of(current), pid):
            self.set_status(tr('Окно изменилось. Текст сохранён здесь — нажмите «Копировать текст».'))
            self.tray.showMessage(tr('Текст готов'), tr('Откройте Dictator, чтобы скопировать результат.'))
            return
        # Avoid triggering a different shortcut if a modifier is currently held.
        if any(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000 for vk in (0x11, 0x12, 0x10, 0x5B, 0x5C)):
            self.set_status(tr('Зажата клавиша-модификатор. Скопируйте результат из окна приложения.'))
            return
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
            finally:
                win32clipboard.CloseClipboard()
            if win32gui.GetForegroundWindow() != hwnd:
                self.set_status(tr('Окно изменилось. Результат находится в буфере обмена.'))
                return
            keyboard.send("ctrl+v")
            self.set_status(error or tr('Текст отправлен в активное поле и оставлен в буфере обмена.'))
        except Exception as exc:
            self.set_status(tr('Автовставка не удалась. Нажмите «Копировать текст». ') + str(exc))

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def quit_app(self):
        if self.busy:
            self.set_status(tr('Дождитесь завершения текущей загрузки или распознавания перед выходом.'))
            self.open_window()
            return
        self.closing = True
        self.unhook()
        if self.stream is not None:
            stream, self.stream = self.stream, None
            try:
                stream.stop()
            except Exception:
                logging.exception('Microphone stop failed during exit')
            finally:
                try:
                    stream.close()
                except Exception:
                    logging.exception('Microphone close failed during exit')
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.tray.hide()
        QtWidgets.QApplication.quit()


def main():
    set_language(get_ui_language())
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    mutex = kernel.CreateMutexW(None, False, "Local\\Diktatoro.Singleton")
    duplicate = ctypes.get_last_error() == 183
    app = QtWidgets.QApplication(sys.argv)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Dictator.Desktop")
    app.setWindowIcon(app_icon())
    app.setQuitOnLastWindowClosed(False)
    if duplicate:
        QtWidgets.QMessageBox.information(None, "Dictator", tr('Приложение уже запущено. Откройте его через значок в трее.'))
        return
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    window = Window()
    if '--startup' not in sys.argv:
        window.show()
    app.exec()
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle(mutex)


if __name__ == "__main__":
    main()
