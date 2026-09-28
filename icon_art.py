"""Code-native pixel art: antique brass carbon microphone on a cast-iron stand."""
import struct
from pathlib import Path
from PySide6 import QtCore, QtGui


def pixel_microphone():
    image = QtGui.QImage(32, 32, QtGui.QImage.Format_ARGB32)
    image.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(image)
    painter.setPen(QtCore.Qt.NoPen)
    def rect(x, y, w, h, color):
        painter.fillRect(x, y, w, h, QtGui.QColor(color))
    outline, brass, gold, light = '#302820', '#987044', '#cfaa65', '#f6d998'
    # Stepped round capsule, like an early carbon microphone.
    rect(11, 1, 10, 1, outline)
    rect(8, 2, 16, 2, outline)
    rect(6, 4, 20, 3, outline)
    rect(5, 7, 22, 8, outline)
    rect(7, 15, 18, 3, outline)
    rect(10, 18, 12, 1, outline)
    rect(10, 3, 12, 1, light)
    rect(8, 4, 16, 3, gold)
    rect(7, 7, 18, 8, brass)
    rect(9, 15, 14, 2, gold)
    rect(11, 17, 10, 1, brass)
    rect(8, 7, 1, 7, light)
    rect(10, 5, 12, 1, light)
    # Dark diaphragm with alternating grille bars.
    rect(10, 6, 12, 10, '#493c31')
    rect(9, 8, 14, 6, '#493c31')
    for y in (7, 9, 11, 13):
        rect(11, y, 10, 1, '#d6b879')
        rect(11, y, 2, 1, light)
    rect(12, 15, 8, 1, '#a18050')
    # Heavy U-shaped bracket, pivots, and decorative stem.
    rect(3, 10, 2, 9, outline)
    rect(27, 10, 2, 9, outline)
    rect(4, 18, 3, 3, outline)
    rect(25, 18, 3, 3, outline)
    rect(6, 20, 20, 2, outline)
    rect(4, 11, 1, 7, gold)
    rect(27, 11, 1, 7, brass)
    rect(5, 18, 2, 2, gold)
    rect(25, 18, 2, 2, brass)
    rect(7, 20, 18, 1, gold)
    rect(3, 10, 4, 3, brass)
    rect(26, 10, 4, 3, brass)
    rect(3, 10, 2, 1, light)
    rect(27, 10, 2, 1, gold)
    rect(13, 22, 6, 1, outline)
    rect(14, 23, 4, 4, outline)
    rect(15, 22, 2, 5, gold)
    rect(15, 23, 1, 3, light)
    rect(12, 26, 8, 2, outline)
    rect(13, 26, 6, 1, brass)
    rect(8, 28, 16, 1, outline)
    rect(6, 29, 20, 2, outline)
    rect(9, 28, 14, 1, gold)
    rect(7, 29, 18, 1, '#59635d')
    rect(9, 29, 5, 1, '#879387')
    painter.end()
    return image


def app_icon(status=None):
    image = brand_image()
    if status is not None:
        p = QtGui.QPainter(image)
        p.scale(image.width() / 96, image.height() / 96)
        p.setPen(QtGui.QPen(QtGui.QColor('#17212f'),5))
        p.setBrush(QtGui.QColor(status))
        p.drawEllipse(72,72,20,20)
        p.end()
    icon = QtGui.QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(QtGui.QPixmap.fromImage(image.scaled(size, size, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)))
    return icon


def brand_image():
    image = QtGui.QImage(str(Path(__file__).parent / 'assets/gold-logo.png'))
    if image.isNull():
        raise RuntimeError('Missing Dictatoro gold logo')
    return image.convertToFormat(QtGui.QImage.Format_ARGB32)


def save_assets(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    original = brand_image()
    original.scaled(256, 256, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation).save(str(folder / 'dictator.png'))
    sizes = (16, 24, 32, 48, 64, 128, 256)
    blobs = []
    for size in sizes:
        data = QtCore.QByteArray()
        buffer = QtCore.QBuffer(data)
        buffer.open(QtCore.QIODevice.WriteOnly)
        original.scaled(size, size, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation).save(buffer, 'PNG')
        blobs.append(bytes(data))
    offset = 6 + 16 * len(sizes)
    entries = []
    for size, blob in zip(sizes, blobs):
        entries.append(struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(blob), offset))
        offset += len(blob)
    (folder / 'dictator.ico').write_bytes(struct.pack('<HHH', 0, 1, len(sizes)) + b''.join(entries) + b''.join(blobs))
