"""Read-only access to notices and included source archives."""
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from i18n import tr


def show_licenses(parent):
    folder = Path(__file__).resolve().parent / 'legal'
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(tr('Лицензии и исходники'))
    dialog.resize(760, 580)
    layout = QtWidgets.QVBoxLayout(dialog)
    browser = QtWidgets.QTextBrowser()
    browser.document().setBaseUrl(QtCore.QUrl.fromLocalFile(str(folder) + '/'))
    browser.setOpenExternalLinks(True)
    notices = folder / 'NOTICES.md'
    browser.setMarkdown(notices.read_text('utf-8') if notices.is_file() else tr('Файлы лицензий не найдены.'))
    layout.addWidget(browser)
    open_folder = QtWidgets.QPushButton(tr('Открыть папку лицензий и исходников'))
    open_folder.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(folder))))
    layout.addWidget(open_folder)
    parent.legal_dialog = dialog
    dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    dialog.show()
