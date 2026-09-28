"""Native Qt desktop interface: sidebar and three independently scrollable pages."""
from PySide6 import QtCore, QtGui, QtWidgets
from core import KEYS, MODELS, LANGUAGES, UI_LANGUAGES, MOUSE_BUTTONS, key_label
from icon_art import app_icon
from i18n import tr


STYLE = '''
QWidget { color:#25332f; font-family:"Segoe UI"; font-size:14px; }
QWidget#shell { background:#f5f3ee; }
QFrame#sidebar { background:#192a28; border:0; }
QFrame#sidebar QLabel { color:#acbab2; background:transparent; }
QFrame#sidebar QLabel#brand { color:#fff4db; font-size:25px; font-weight:700; }
QFrame#sidebar QLabel#brandSub { color:#a9bab2; font-size:12px; }
QPushButton#nav { text-align:left; background:transparent; color:#becbc4; border:0; border-radius:9px; padding:14px 16px; font-weight:600; }
QPushButton#nav:hover { background:#243b35; color:white; }
QPushButton#nav:checked { background:#344b41; color:#f3d5a0; }
QPushButton#trayButton { background:transparent; color:#aabdb2; border:1px solid #41564c; border-radius:8px; padding:11px; }
QLabel#pageTitle { font-size:30px; font-weight:700; color:#20392e; }
QLabel#eyebrow { color:#8e6c41; font-size:11px; font-weight:700; }
QLabel#muted { color:#738078; font-size:12px; }
QLabel#sectionTitle { color:#2a3a30; font-size:16px; font-weight:600; }
QLabel#pill { background:#e8eddf; color:#4d634e; border-radius:12px; padding:6px 11px; font-size:11px; font-weight:600; }
QFrame#card { background:white; border:1px solid #e4e5dc; border-radius:14px; }
QFrame#recordCard { background:#eaf0e5; border:1px solid #dbe4d4; border-radius:16px; }
QLabel#status { color:#53604f; font-size:13px; }
QLabel#fieldLabel { font-size:12px; font-weight:600; color:#6a7468; }
QComboBox { background:#f8f8f4; border:1px solid #dedfd5; border-radius:7px; min-height:23px; padding:8px 12px; }
QComboBox:hover { border-color:#b7c3b0; }
QComboBox:focus { border:1px solid #73906c; }
QComboBox:disabled { color:#9a9f92; background:#f1f1ec; }
QComboBox::drop-down { width:25px; border:0; }
QComboBox QAbstractItemView { background:white; color:#25332f; border:1px solid #dadfd4; selection-background-color:#e5eddd; selection-color:#233b2d; }
QPushButton { background:#f5f5ef; border:1px solid #dcdfd2; border-radius:8px; padding:10px 15px; font-weight:600; }
QPushButton:hover { background:#e9eddf; border-color:#c4cdb7; }
QPushButton:disabled { color:#a5ac9d; background:#f0f1e9; }
QPushButton#record { background:#264733; color:white; border:0; border-radius:11px; min-height:34px; padding:13px 20px; font-size:15px; }
QPushButton#record:hover { background:#355e42; }
QPushButton#record:disabled { background:#b2c0ab; color:#ffffff; }
QPushButton#record[recording="true"] { background:#a74738; }
QPlainTextEdit { background:#fcfcf8; border:1px solid #e5e6dc; border-radius:9px; padding:12px; font-size:15px; selection-background-color:#dce9ce; }
QProgressBar { background:#d7e0ce; border:0; border-radius:3px; min-height:6px; max-height:6px; }
QProgressBar::chunk { background:#698453; border-radius:3px; }
QScrollArea { border:0; background:transparent; }
QScrollArea > QWidget > QWidget { background:transparent; }
QScrollBar:vertical { background:transparent; width:8px; margin:6px 0; }
QScrollBar::handle:vertical { background:#ccd2c5; border-radius:4px; min-height:28px; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical { background:transparent; }
QMenu { background:white; padding:6px; border:1px solid #dcded3; }
QMenu::item { padding:8px 22px; }
QMenu::item:selected { background:#e9efdf; }
QDialog { background:#f5f3ee; }
QToolTip { background:#233a2d; color:white; padding:7px; border:0; }
'''


class Switch(QtWidgets.QCheckBox):
    def __init__(self, label):
        super().__init__()
        self.setAccessibleName(label)
        self.setToolTip(label)
        self.setFixedSize(48,30)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def paintEvent(self, event):
        p=QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setPen(QtCore.Qt.NoPen)
        p.setBrush(QtGui.QColor('#54734c' if self.isChecked() else '#cbd2c5'))
        p.drawRoundedRect(0,3,48,24,12,12)
        x=26 if self.isChecked() else 4
        if self.layoutDirection()==QtCore.Qt.RightToLeft:
            x=48-x-18
        p.setBrush(QtGui.QColor('white'))
        p.drawEllipse(x,6,18,18)
        if self.hasFocus():
            p.setPen(QtGui.QPen(QtGui.QColor('#9baf8b'),1))
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawRoundedRect(1,1,46,28,13,13)
        p.end()

    def hitButton(self, pos):
        return self.rect().contains(pos)


def label(text, role=None):
    widget=QtWidgets.QLabel(text)
    widget.setWordWrap(True)
    if role: widget.setObjectName(role)
    return widget


def card(role='card'):
    widget=QtWidgets.QFrame()
    widget.setObjectName(role)
    layout=QtWidgets.QVBoxLayout(widget)
    layout.setContentsMargins(24,22,24,22)
    layout.setSpacing(14)
    return widget,layout


def field(layout, text, widget):
    group=QtWidgets.QVBoxLayout()
    group.setSpacing(7)
    group.addWidget(label(text,'fieldLabel'))
    group.addWidget(widget)
    layout.addLayout(group)


def page(title, subtitle, rtl):
    scroll=QtWidgets.QScrollArea()
    scroll.setWidgetResizable(True)
    content=QtWidgets.QWidget()
    content.setLayoutDirection(QtCore.Qt.RightToLeft if rtl else QtCore.Qt.LeftToRight)
    layout=QtWidgets.QVBoxLayout(content)
    layout.setContentsMargins(34,28,34,24)
    layout.setSpacing(20)
    layout.addWidget(label(title,'pageTitle'))
    layout.addWidget(label(subtitle,'muted'))
    scroll.setWidget(content)
    return scroll,layout


def build_ui(w, result='', index=0):
    w.ui_building=True
    if not hasattr(w,'outer_layout'):
        w.outer_layout=QtWidgets.QVBoxLayout(w)
        w.outer_layout.setContentsMargins(0,0,0,0)
    elif hasattr(w,'shell'):
        w.outer_layout.removeWidget(w.shell)
        w.shell.hide()
        w.shell.deleteLater()
    w.shell=QtWidgets.QWidget()
    w.shell.setObjectName('shell')
    w.shell.setLayoutDirection(QtCore.Qt.LeftToRight) # Sidebar stays on the left in every language.
    root=QtWidgets.QHBoxLayout(w.shell)
    root.setContentsMargins(0,0,0,0)
    root.setSpacing(0)
    w.outer_layout.addWidget(w.shell)
    side=QtWidgets.QFrame()
    side.setObjectName('sidebar')
    side.setFixedWidth(210)
    s=QtWidgets.QVBoxLayout(side)
    s.setContentsMargins(18,30,18,24)
    s.setSpacing(9)
    brandrow=QtWidgets.QHBoxLayout()
    icon=QtWidgets.QLabel()
    icon.setPixmap(app_icon().pixmap(38,38))
    brandrow.addWidget(icon)
    brandrow.addWidget(label('Dictator','brand'))
    s.addLayout(brandrow)
    s.addWidget(label(tr('Голос становится текстом'),'brandSub'))
    s.addSpacing(34)
    w.pages=QtWidgets.QStackedWidget()
    w.nav_buttons=[]
    for i,(symbol,text) in enumerate((('⌂',tr('Главная')),('⚙',tr('Настройки')),('ⓘ',tr('О проекте')))):
        button=QtWidgets.QPushButton(symbol+'   '+text)
        button.setObjectName('nav')
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False,n=i:w.navigate(n))
        s.addWidget(button)
        w.nav_buttons.append(button)
    s.addStretch()
    s.addWidget(label(tr('Локально. На вашем компьютере.'),'brandSub'))
    tray=QtWidgets.QPushButton(tr('Свернуть в трей'))
    tray.setObjectName('trayButton')
    tray.clicked.connect(w.hide)
    s.addWidget(tray)
    s.addSpacing(10)
    s.addWidget(label('VERSION 0.3','brandSub'))
    root.addWidget(side)
    root.addWidget(w.pages,1)
    rtl=w.config['ui_language']=='ar'

    home,h=page(tr('Ваш голос. Ваши слова.'),tr('Говорите свободно — Dictator запишет за вас.'),rtl)
    recorder,r=card('recordCard')
    heading=QtWidgets.QHBoxLayout()
    heading.addWidget(label(tr('Голосовой ввод'),'sectionTitle'))
    heading.addStretch()
    heading.addWidget(label(tr('ЛОКАЛЬНО'),'pill'))
    r.addLayout(heading)
    w.status=label(tr('Загрузите модель, чтобы начать'),'status')
    r.addWidget(w.status)
    w.meter=QtWidgets.QProgressBar()
    w.meter.setRange(0,100)
    w.meter.setValue(0)
    w.meter.setTextVisible(False)
    w.meter.setAccessibleName(tr('Уровень микрофона'))
    r.addWidget(w.meter)
    w.record_button=QtWidgets.QPushButton('●  '+tr('Начать запись'))
    w.record_button.setObjectName('record')
    w.record_button.clicked.connect(w.toggle_recording)
    r.addWidget(w.record_button)
    r.addWidget(label(tr('Запись появится здесь. Для ввода в другом приложении удерживайте назначенную кнопку.'),'muted'))
    h.addWidget(recorder)
    controls,c=card()
    c.addWidget(label(tr('Параметры диктовки'),'sectionTitle'))
    w.key_box=QtWidgets.QComboBox()
    for key in KEYS: w.key_box.addItem(key_label(key),key)
    w.mouse_names={'middle':tr('Мышь: нажатие колеса'),'x1':tr('Мышь: боковая кнопка 1'),'x2':tr('Мышь: боковая кнопка 2')}
    for button in MOUSE_BUTTONS: w.key_box.addItem(w.mouse_names[button],{'mouse':button})
    if isinstance(w.config['key'],dict) and 'mouse' not in w.config['key']:
        w.key_box.addItem(key_label(w.config['key']),w.config['key'])
    w.key_box.setCurrentIndex(w.key_box.findData(w.config['key']))
    trigger=QtWidgets.QHBoxLayout()
    trigger.addWidget(w.key_box,1)
    w.custom_button=QtWidgets.QPushButton(tr('Назначить…'))
    w.custom_button.clicked.connect(w.choose_key)
    trigger.addWidget(w.custom_button)
    c.addWidget(label(tr('Клавиатура или мышь'),'fieldLabel'))
    c.addLayout(trigger)
    grid=QtWidgets.QHBoxLayout()
    w.model_box=QtWidgets.QComboBox()
    w.model_box.addItems(MODELS)
    w.model_box.setCurrentText(w.config['model'])
    field(grid,tr('Модель Whisper'),w.model_box)
    w.lang_box=QtWidgets.QComboBox()
    for code in LANGUAGES:
        name=tr('Автоматически') if code=='auto' else UI_LANGUAGES.get(code,{'uk':'Українська'}.get(code,code))
        w.lang_box.addItem(name,code)
    w.lang_box.setCurrentIndex(w.lang_box.findData(w.config['language']))
    field(grid,tr('Язык речи'),w.lang_box)
    c.addLayout(grid)
    w.device_box=QtWidgets.QComboBox()
    w.device_box.addItem(tr('Системный микрофон'),None)
    w.populate_microphones()
    field(c,tr('Микрофон'),w.device_box)
    bottom=QtWidgets.QHBoxLayout()
    bottom.addWidget(label(tr('Модель скачивается один раз. Аудио остаётся на компьютере.'),'muted'),1)
    w.apply_button=QtWidgets.QPushButton(tr('Загрузить модель'))
    w.apply_button.clicked.connect(w.apply)
    bottom.addWidget(w.apply_button)
    c.addLayout(bottom)
    h.addWidget(controls)
    output,o=card()
    row=QtWidgets.QHBoxLayout()
    row.addWidget(label(tr('Последний результат'),'sectionTitle'))
    row.addStretch()
    copy=QtWidgets.QPushButton(tr('Копировать текст'))
    copy.clicked.connect(lambda:QtWidgets.QApplication.clipboard().setText(w.text.toPlainText()))
    row.addWidget(copy)
    o.addLayout(row)
    w.text=QtWidgets.QPlainTextEdit()
    w.text.setPlaceholderText(tr('Здесь появится распознанный текст'))
    w.text.setMinimumHeight(100)
    w.text.setMaximumHeight(170)
    w.text.setPlainText(result)
    o.addWidget(w.text)
    h.addWidget(output)
    h.addStretch()
    w.pages.addWidget(home)

    settings,p=page(tr('Настройки'),tr('Пусть Dictator работает так, как удобно вам.'),rtl)
    preferences,v=card()
    v.addWidget(label(tr('Язык и запуск'),'sectionTitle'))
    w.ui_language_box=QtWidgets.QComboBox()
    for code,name in UI_LANGUAGES.items(): w.ui_language_box.addItem(name,code)
    w.ui_language_box.setCurrentIndex(w.ui_language_box.findData(w.config['ui_language']))
    field(v,tr('Язык интерфейса'),w.ui_language_box)
    v.addWidget(label(tr('Изменения применяются сразу и сохраняются автоматически.'),'muted'))
    v.addSpacing(16)
    startuprow=QtWidgets.QHBoxLayout()
    startuptext=QtWidgets.QVBoxLayout()
    startuptext.addWidget(label(tr('Запускать при входе в Windows'),'sectionTitle'))
    startuptext.addWidget(label(tr('Приложение будет работать в фоне, доступ через значок в трее'),'muted'))
    startuprow.addLayout(startuptext,1)
    w.startup_box=Switch(tr('Запускать при входе в Windows'))
    w.startup_box.setChecked(w.read_autostart())
    startuprow.addWidget(w.startup_box)
    v.addLayout(startuprow)
    translationrow=QtWidgets.QHBoxLayout()
    translationtext=QtWidgets.QVBoxLayout()
    translationtext.addWidget(label(tr('Переводить речь на английский'),'sectionTitle'))
    translationtext.addWidget(label(tr('Локально. Язык речи выбирается на главной. Для качества рекомендуется medium.'),'muted'))
    translationrow.addLayout(translationtext,1)
    w.translation_box=Switch(tr('Переводить речь на английский'))
    w.translation_box.setChecked(w.config['translate_to_english'])
    translationrow.addWidget(w.translation_box)
    v.addLayout(translationrow)
    p.addWidget(preferences)
    w.settings_status=label('', 'muted')
    p.addWidget(w.settings_status)
    p.addStretch()
    w.pages.addWidget(settings)

    about,a=page(tr('О проекте'),tr('Небольшой проект. Большая вера в доступные инструменты.'),rtl)
    story,b=card()
    b.addWidget(label(tr('История проекта'),'sectionTitle'))
    from story import STORY
    for paragraph in STORY[w.config['ui_language']]:
        text=label(paragraph)
        text.setStyleSheet('font-size:15px; color:#4b594f;')
        b.addWidget(text)
        b.addSpacing(4)
    a.addWidget(story)
    a.addWidget(label('Dictator 0.3', 'muted'))
    from legal_view import show_licenses
    licenses = QtWidgets.QPushButton(tr('Лицензии и исходники'))
    licenses.clicked.connect(lambda: show_licenses(w))
    a.addWidget(licenses)
    a.addStretch()
    w.pages.addWidget(about)
    for widget in (w.key_box,w.model_box,w.lang_box,w.device_box):
        widget.currentIndexChanged.connect(w.on_preferences_changed)
    w.ui_language_box.currentIndexChanged.connect(w.change_language)
    w.startup_box.toggled.connect(w.change_autostart)
    w.translation_box.toggled.connect(w.on_preferences_changed)
    w.navigate(index)
    w.ui_building=False
