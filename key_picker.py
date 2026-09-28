from i18n import tr
"""Capture one physical keyboard key, committing only after its release."""
import os
import keyboard
import win32gui
import win32process
from PySide6 import QtCore, QtWidgets
from core import key_label, matches_custom


class KeyPicker(QtWidgets.QDialog):
    captured = QtCore.Signal(object, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Назначить кнопку'))
        self.setMinimumWidth(480)
        self.selection = None
        self.pending = None
        self.active = False
        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(tr('Наведите указатель на это окно и нажмите колесо или боковую кнопку мыши. Или нажмите любую клавишу клавиатуры.'))
        self.label.setMinimumHeight(90)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        hint = QtWidgets.QLabel(tr('Выбранная клавиша будет занята диктовкой.\nОтмена — кнопкой ниже. Ожидание: 20 секунд.'))
        hint.setWordWrap(True)
        layout.addWidget(hint)
        cancel = QtWidgets.QPushButton(tr('Отмена'))
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)
        self.captured.connect(self.on_capture)
        self.timeout = QtCore.QTimer(self)
        self.timeout.setSingleShot(True)
        self.timeout.timeout.connect(self.reject)

    def capture_event(self, event):
        if not self.active:
            return True
        try:
            if win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[1] != os.getpid():
                return True
        except Exception:
            return True
        if self.pending is None and event.event_type == "down":
            self.pending = {"scan_code": event.scan_code,
                "name": event.name or (tr('Клавиша ') + str(event.scan_code)), "is_keypad": bool(event.is_keypad)}
            self.captured.emit(self.pending, False)
        if self.pending is not None and 'mouse' not in self.pending and matches_custom(self.pending, event):
            if event.event_type == "up":
                self.active = False
                self.captured.emit(self.pending, True)
            return False
        return True

    def on_capture(self, value, released):
        name = tr({'middle': 'Мышь: нажатие колеса', 'x1': 'Мышь: боковая кнопка 1', 'x2': 'Мышь: боковая кнопка 2'}[value['mouse']]) if 'mouse' in value else key_label(value)
        self.label.setText(tr('Выбрана: ') + name + tr('\nОтпустите кнопку…'))
        if released:
            self.selection = value
            self.accept()

    def keyPressEvent(self, event):
        # Escape and Enter can themselves be assigned; cancel is a mouse button.
        event.accept()

    def keyReleaseEvent(self, event):
        event.accept()

    def eventFilter(self, watched, event):
        if not self.active or not isinstance(watched, QtWidgets.QWidget):
            return False
        if watched is not self and not self.isAncestorOf(watched):
            return False
        if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
            button = {QtCore.Qt.MiddleButton:'middle', QtCore.Qt.BackButton:'x1', QtCore.Qt.ForwardButton:'x2'}.get(event.button())
            if button:
                down = event.type() == QtCore.QEvent.MouseButtonPress
                if self.pending is None and down:
                    self.pending = {'mouse': button}
                if self.pending == {'mouse': button}:
                    self.on_capture(self.pending, not down)
                return True
        return False

    def choose(self):
        hook = None
        try:
            self.active = True
            QtWidgets.QApplication.instance().installEventFilter(self)
            hook = keyboard.hook(self.capture_event, suppress=True)
            self.timeout.start(20000)
            return self.selection if self.exec() == QtWidgets.QDialog.Accepted else None
        finally:
            self.active = False
            QtWidgets.QApplication.instance().removeEventFilter(self)
            self.timeout.stop()
            if hook is not None:
                keyboard.unhook(hook)
