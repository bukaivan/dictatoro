"""Compact Dictatoro desktop UI. Existing controller owns recording and persistence."""
from pathlib import Path
import math
from PySide6 import QtCore, QtGui, QtWidgets
from core import KEYS, MODELS, LANGUAGES, UI_LANGUAGES, key_label
from i18n import tr
from ui import Switch as BaseSwitch

class Switch(BaseSwitch):
    def paintEvent(self,event):
        p=QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.Antialiasing); p.setPen(QtCore.Qt.NoPen)
        p.setBrush(QtGui.QColor('#cba54c' if self.isChecked() else '#555952')); p.drawRoundedRect(0,3,48,24,12,12)
        x=26 if self.isChecked() else 4
        if self.layoutDirection()==QtCore.Qt.RightToLeft:x=48-x-18
        p.setBrush(QtGui.QColor('#faf7ef')); p.drawEllipse(x,6,18,18)
        if self.hasFocus():
            p.setPen(QtGui.QPen(QtGui.QColor('#e5bf59'),1)); p.setBrush(QtCore.Qt.NoBrush);p.drawRoundedRect(1,1,46,28,13,13)
        p.end()

STYLE = '''
QWidget {color:#f0f0eb;font-family:"Segoe UI";font-size:13px;}
QWidget#shell,QDialog {background:#1d1e20;}
QFrame#sidebar {background:#191a1c;}
QLabel#title {font-size:22px;font-weight:600;}
QLabel#muted,QLabel#fieldLabel {color:#b2b4ae;font-size:12px;}
QFrame#panel {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #303235,stop:1 #26282b);border:1px solid #414345;border-radius:16px;}
QPushButton {background:#303235;border:1px solid #4b4d4e;border-radius:10px;padding:8px 12px;}
QPushButton:hover {background:#3b3d40;border-color:#b79542;}
QPushButton:focus,QComboBox:focus {border:2px solid #e5bf59;}
QPushButton:disabled {color:#8d8e88;background:#333431;border-color:#414345;}
QPushButton#nav {padding:0;border-radius:13px;background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #514b3d,stop:1 #323232);border:1px solid #625a46;}
QPushButton#nav:checked {background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #bba365,stop:1 #796130);border-color:#dfc685;}
QPushButton#record {color:#242622;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #f3dc96,stop:.5 #e7c363,stop:1 #cfa047);border:1px solid #f7e4ae;border-radius:24px;font-weight:600;}
QPushButton#record:disabled {background:#514c3b;color:#c2bca9;border-color:#6c6348;}
QPushButton#record[recording="true"] {background:#e6aca0;border-color:#edc2b7;color:#34211f;}
QPushButton#model {padding:8px 4px;border-radius:12px;}
QPushButton#model:checked {background:#433a25;color:#f4d788;border-color:#b79542;}
QComboBox {background:#2d2f32;border:1px solid #4b4d4e;border-radius:12px;padding:8px 12px;min-height:22px;}
QComboBox::drop-down {border:0;width:20px;}
QComboBox QAbstractItemView {background:#282a2d;color:#f0f0eb;selection-background-color:#514731;selection-color:#f4d788;}
QPlainTextEdit,QTextBrowser {background:#26282b;color:#f0f0eb;border:1px solid #414345;border-radius:8px;padding:8px;selection-background-color:#75602c;}
QProgressBar {border:0;background:#414345;max-height:3px;min-height:3px;}
QProgressBar::chunk {background:#e5bf59;}
QMenu {background:#282a2d;color:#f0f0eb;border:1px solid #414345;}
QMenu::item {padding:8px 20px;} QMenu::item:selected {background:#514731;}
QToolTip {background:#303235;color:#f0f0eb;border:1px solid #6c6348;padding:6px;}
'''

def label(text, role='muted'):
    w = QtWidgets.QLabel(text)
    w.setWordWrap(True)
    w.setObjectName(role)
    return w

def panel():
    w = QtWidgets.QFrame(); w.setObjectName('panel')
    v = QtWidgets.QVBoxLayout(w); v.setContentsMargins(16,12,16,12); v.setSpacing(10)
    return w,v

def nav_icon(index):
    pix = QtGui.QPixmap(44,44); pix.fill(QtCore.Qt.transparent)
    p = QtGui.QPainter(pix); p.setRenderHint(QtGui.QPainter.Antialiasing)
    p.scale(2,2); p.setPen(QtGui.QPen(QtGui.QColor('#fff4da'),1.6,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
    if index == 0:
        path = QtGui.QPainterPath()
        path.moveTo(2.5, 10); path.lineTo(11, 3); path.lineTo(19.5, 10)
        path.moveTo(4, 9); path.lineTo(4, 17.5)
        path.quadTo(4, 19, 5.5, 19)
        path.lineTo(8.5, 19); path.lineTo(8.5, 13)
        path.lineTo(13.5, 13); path.lineTo(13.5, 19)
        path.lineTo(16.5, 19); path.quadTo(18, 19, 18, 17.5)
        path.lineTo(18, 9); p.drawPath(path)
    elif index == 1:
        # One continuous toothed outline, with a clear central opening.
        path = QtGui.QPainterPath()
        for tooth in range(8):
            for offset, radius in ((-22.5, 6.5), (-12, 8.3), (12, 8.3), (22.5, 6.5)):
                angle = math.radians(tooth * 45 + offset)
                point = QtCore.QPointF(11 + radius * math.cos(angle), 11 + radius * math.sin(angle))
                if tooth == 0 and offset == -22.5: path.moveTo(point)
                else: path.lineTo(point)
        path.closeSubpath(); p.drawPath(path)
        p.drawEllipse(QtCore.QRectF(8, 8, 6, 6))
    else:
        p.drawEllipse(QtCore.QRectF(3,3,16,16)); p.drawLine(11,10,11,16); p.drawPoint(11,7)
    p.end(); return QtGui.QIcon(pix)

class NavigationButton(QtWidgets.QPushButton):
    """Layered gold and glass tile from the approved sidebar mockup."""
    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        active = self.isChecked()
        back = QtGui.QLinearGradient(4, 0, 44, 40)
        back.setColorAt(0, QtGui.QColor('#d6b769' if active else '#48463f'))
        back.setColorAt(1, QtGui.QColor('#947330' if active else '#2d2f30'))
        p.setPen(QtCore.Qt.NoPen); p.setBrush(back)
        p.drawRoundedRect(QtCore.QRectF(4, 0, 39, 39), 12, 12)
        face = QtGui.QLinearGradient(0, 3, 40, 43)
        face.setColorAt(0, QtGui.QColor('#55fff7db' if active else '#24ffffff'))
        face.setColorAt(.55, QtGui.QColor('#25ffe5a3' if active else '#12ffffff'))
        face.setColorAt(1, QtGui.QColor('#40f8df89' if active else '#14dec589'))
        p.setBrush(face)
        p.setPen(QtGui.QPen(QtGui.QColor('#bbf5df9b' if active or self.underMouse() else '#35e7dbb3'), 1))
        p.drawRoundedRect(QtCore.QRectF(.5, 3.5, 39, 39), 13, 13)
        p.setBrush(QtCore.Qt.NoBrush)
        p.setPen(QtGui.QPen(QtGui.QColor('#30ffffff'), .8))
        p.drawRoundedRect(QtCore.QRectF(1.5, 4.5, 37, 37), 12, 12)
        self.icon().paint(p, QtCore.QRect(9, 12, 22, 22))
        if self.hasFocus():
            p.setPen(QtGui.QPen(QtGui.QColor('#fff4da'), 1, QtCore.Qt.DotLine))
            p.drawRoundedRect(QtCore.QRectF(2, 5, 36, 36), 11, 11)
        p.end()


class ModelButtons(QtWidgets.QWidget):
    currentIndexChanged = QtCore.Signal(int)
    def __init__(self, selected):
        super().__init__(); self.value=selected
        h=QtWidgets.QHBoxLayout(self); h.setContentsMargins(0,0,0,0); h.setSpacing(8)
        self.buttons=[]
        for name in MODELS:
            b=QtWidgets.QPushButton(name.title()); b.setObjectName('model'); b.setCheckable(True); b.setChecked(name==selected)
            b.setMinimumHeight(36); b.clicked.connect(lambda checked=False,n=name:self.select(n)); h.addWidget(b); self.buttons.append(b)
    def currentText(self): return self.value
    def select(self,name):
        changed=name!=self.value; self.value=name
        for n,b in zip(MODELS,self.buttons): b.setChecked(n==name)
        if changed:self.currentIndexChanged.emit(MODELS.index(name))

def build_ui(w,result='',index=0):
    w.ui_building=True
    if not hasattr(w,'outer_layout'):
        w.outer_layout=QtWidgets.QVBoxLayout(w); w.outer_layout.setContentsMargins(0,0,0,0)
    else:
        w.outer_layout.removeWidget(w.shell); w.shell.hide(); w.shell.deleteLater()
    w.shell=QtWidgets.QWidget(); w.shell.setObjectName('shell'); w.shell.setLayoutDirection(QtCore.Qt.LeftToRight)
    outer=QtWidgets.QVBoxLayout(w.shell); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0); w.outer_layout.addWidget(w.shell)
    body=QtWidgets.QHBoxLayout(); body.setSpacing(0); outer.addLayout(body,1)
    side=QtWidgets.QFrame(); side.setObjectName('sidebar'); side.setFixedWidth(64)
    sv=QtWidgets.QVBoxLayout(side); sv.setContentsMargins(10,16,10,16); sv.setSpacing(12)
    w.nav_buttons=[]
    for n,title in enumerate((tr('Главная'),tr('Настройки'),tr('О проекте'))):
        b=NavigationButton(); b.setObjectName('nav'); b.setFixedSize(44,44); b.setIcon(nav_icon(n)); b.setIconSize(QtCore.QSize(22,22)); b.setCheckable(True); b.setToolTip(title); b.setAccessibleName(title); b.clicked.connect(lambda checked=False,i=n:w.navigate(i)); sv.addWidget(b); w.nav_buttons.append(b)
    sv.addStretch(); sv.addWidget(label('v0.3')); body.addWidget(side)
    w.pages=QtWidgets.QStackedWidget(); body.addWidget(w.pages,1)
    def page(title=None):
        widget=QtWidgets.QWidget(); widget.setLayoutDirection(QtCore.Qt.RightToLeft if w.config['ui_language']=='ar' else QtCore.Qt.LeftToRight)
        v=QtWidgets.QVBoxLayout(widget); v.setContentsMargins(20,16,20,16); v.setSpacing(12)
        if title:v.addWidget(label(title,'title'))
        w.pages.addWidget(widget); return v
    home=page(); rec,r=panel(); home.addWidget(rec)
    w.status=label(tr('Загрузите модель, чтобы начать')); r.addWidget(w.status)
    w.record_button=QtWidgets.QPushButton(tr('Начать запись')); w.record_button.setObjectName('record'); w.record_button.setMinimumHeight(48)
    w.record_button.setIcon(QtGui.QIcon(str(Path(__file__).parent/'assets/wordmark-symbol.png'))); w.record_button.setIconSize(QtCore.QSize(24,24)); w.record_button.clicked.connect(w.toggle_recording); r.addWidget(w.record_button)
    w.trigger_hint=label(''); w.trigger_hint.setAlignment(QtCore.Qt.AlignCenter); r.addWidget(w.trigger_hint)
    w.meter=QtWidgets.QProgressBar(); w.meter.setRange(0,100); w.meter.setValue(0); w.meter.setTextVisible(False); w.meter.hide()
    resultrow=QtWidgets.QHBoxLayout(); resultrow.addWidget(label(tr('Последний результат'))); resultrow.addStretch()
    copy=QtWidgets.QPushButton(tr('Копировать текст')); copy.clicked.connect(lambda:QtWidgets.QApplication.clipboard().setText(w.text.toPlainText())); resultrow.addWidget(copy); r.addLayout(resultrow)
    w.text=QtWidgets.QPlainTextEdit(); w.text.setPlaceholderText(tr('Здесь появится распознанный текст')); w.text.setPlainText(result); w.text.setFixedHeight(64); r.addWidget(w.text)
    fields=QtWidgets.QHBoxLayout(); fields.setSpacing(16); home.addLayout(fields)
    def field(h,title,control):
        v=QtWidgets.QVBoxLayout(); v.setSpacing(6); v.addWidget(label(title,'fieldLabel')); v.addWidget(control); h.addLayout(v,1)
    w.lang_box=QtWidgets.QComboBox()
    for code in LANGUAGES:w.lang_box.addItem(tr('Автоматически') if code=='auto' else UI_LANGUAGES.get(code,{'uk':'Українська'}.get(code,code)),code)
    w.lang_box.setCurrentIndex(w.lang_box.findData(w.config['language'])); field(fields,tr('Язык речи'),w.lang_box)
    w.device_box=QtWidgets.QComboBox(); w.device_box.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon); w.device_box.setMinimumContentsLength(10); w.device_box.addItem(tr('Системный микрофон'),None); w.populate_microphones(); field(fields,tr('Микрофон'),w.device_box)
    home.addWidget(label(tr('Модель Whisper'),'fieldLabel')); w.model_box=ModelButtons(w.config['model']); home.addWidget(w.model_box)
    bottom=QtWidgets.QHBoxLayout(); w.mode_hint=label(''); bottom.addWidget(w.mode_hint,1)
    w.apply_button=QtWidgets.QPushButton(tr('Загрузить модель')); w.apply_button.clicked.connect(w.apply); bottom.addWidget(w.apply_button); home.addLayout(bottom); home.addStretch()
    settings=page(tr('Настройки')); box,v=panel(); settings.addWidget(box)
    v.addWidget(label(tr('Клавиатура или мышь'),'fieldLabel')); keys=QtWidgets.QHBoxLayout()
    w.key_box=QtWidgets.QComboBox()
    for k in KEYS:w.key_box.addItem(key_label(k),k)
    w.mouse_names={'middle':tr('Мышь: нажатие колеса'),'x1':tr('Мышь: боковая кнопка 1'),'x2':tr('Мышь: боковая кнопка 2')}
    for k,title in w.mouse_names.items():w.key_box.addItem(title,{'mouse':k})
    if isinstance(w.config['key'],dict) and 'mouse' not in w.config['key']:w.key_box.addItem(key_label(w.config['key']),w.config['key'])
    w.key_box.setCurrentIndex(w.key_box.findData(w.config['key'])); keys.addWidget(w.key_box,1)
    w.custom_button=QtWidgets.QPushButton(tr('Назначить…')); w.custom_button.clicked.connect(w.choose_key); keys.addWidget(w.custom_button); v.addLayout(keys)
    def switchrow(title,description,checked):
        h=QtWidgets.QHBoxLayout(); texts=QtWidgets.QVBoxLayout(); texts.setSpacing(3); texts.addWidget(label(title,'body'))
        if description:texts.addWidget(label(description))
        h.addLayout(texts,1); switch=Switch(title); switch.setChecked(checked); h.addWidget(switch); v.addSpacing(6); v.addLayout(h); return switch
    w.translation_box=switchrow(tr('Переводить речь на английский'),tr('Локально. Язык речи выбирается на главной. Для качества рекомендуется medium.'),w.config['translate_to_english'])
    v.addWidget(label(tr('Язык интерфейса'),'fieldLabel')); w.ui_language_box=QtWidgets.QComboBox()
    for code,title in UI_LANGUAGES.items():w.ui_language_box.addItem(title,code)
    w.ui_language_box.setCurrentIndex(w.ui_language_box.findData(w.config['ui_language'])); v.addWidget(w.ui_language_box)
    w.startup_box=switchrow(tr('Запускать при входе в Windows'),tr('Приложение будет работать в фоне, доступ через значок в трее'),w.read_autostart())
    def edit_vocabulary():
        dialog = QtWidgets.QDialog(w); dialog.setWindowTitle(tr('Личный словарь')); dialog.resize(440, 380)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(label(tr('Имена и термины, по одному на строку. Подсказки для диктовки, не для перевода.')))
        editor = QtWidgets.QPlainTextEdit(w.config.get('vocabulary', '')); layout.addWidget(editor)
        error = label(''); layout.addWidget(error)
        preset = QtWidgets.QPushButton(tr('Добавить популярные английские слова'))
        layout.addWidget(preset)
        def add_preset():
            from core import add_english_terms
            try:
                editor.setPlainText(add_english_terms(editor.toPlainText()))
                error.setText('')
            except ValueError:
                error.setText(tr('Не более 1000 символов.'))
        preset.clicked.connect(add_preset)
        save = QtWidgets.QPushButton(tr('Сохранить')); layout.addWidget(save)
        def commit():
            from core import validate_config
            if len(editor.toPlainText()) > 1000:
                error.setText(tr('Не более 1000 символов.')); return
            previous = w.config.get('vocabulary', '')
            w.config['vocabulary'] = validate_config({'vocabulary': editor.toPlainText()})['vocabulary']
            try: w.persist()
            except Exception as exc:
                w.config['vocabulary'] = previous; error.setText(str(exc)); return
            dialog.accept()
        save.clicked.connect(commit); dialog.exec()
    vocabulary_button = QtWidgets.QPushButton(tr('Личный словарь')); vocabulary_button.clicked.connect(edit_vocabulary)
    settings.addWidget(vocabulary_button)
    w.settings_status=label(''); settings.addWidget(w.settings_status); settings.addStretch()
    about=page(tr('О проекте')); about.addWidget(label(tr('Ваш голос, ваша независимость.')))
    box,v=panel(); about.addWidget(box)
    from story import STORY
    v.addWidget(label(STORY[w.config['ui_language']][0],'body'))
    email=QtWidgets.QLabel('<a style="color:#e5bf59" href="mailto:dictatoro.app@gmail.com">dictatoro.app@gmail.com</a>'); email.setOpenExternalLinks(True); v.addWidget(email)
    def show_story():
        dialog=QtWidgets.QDialog(w); dialog.setWindowTitle(tr('История проекта')); dialog.resize(560,430); layout=QtWidgets.QVBoxLayout(dialog)
        text=QtWidgets.QTextBrowser(); text.setPlainText('\n\n'.join(STORY[w.config['ui_language']])); layout.addWidget(text); dialog.exec()
    story=QtWidgets.QPushButton(tr('История проекта')); story.clicked.connect(show_story); v.addWidget(story)
    from legal_view import show_licenses
    licenses=QtWidgets.QPushButton(tr('Лицензии и исходники')); licenses.clicked.connect(lambda:show_licenses(w)); v.addWidget(licenses); about.addStretch()
    for control in (w.key_box,w.model_box,w.lang_box,w.device_box):control.currentIndexChanged.connect(w.on_preferences_changed)
    w.translation_box.toggled.connect(w.on_preferences_changed); w.ui_language_box.currentIndexChanged.connect(w.change_language); w.startup_box.toggled.connect(w.change_autostart)
    w.navigate(index); w.ui_building=False; update_hints(w); w.tick()

def update_hints(w):
    w.trigger_hint.setText(tr('Удерживайте ') + w.trigger_label())
    w.mode_hint.setText(tr('Переводить речь на английский') if w.config['translate_to_english'] else tr('Локально. На вашем компьютере.'))
    if w.config['model'] == 'base' and not w.config['translate_to_english']:
        from model_assets import bundled_base_path
        if bundled_base_path() is not None:
            w.mode_hint.setText(tr('Base уже в комплекте. Работает без интернета.'))
