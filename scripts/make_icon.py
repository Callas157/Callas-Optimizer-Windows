"""Gera o ICO multirresolucao da Fênix a partir do SVG versionado.
O ICO e usado pelo executavel, Setup, menu Iniciar e atalho do desktop.
"""
from __future__ import annotations
import os
from pathlib import Path
import struct
from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

SIZES = (16, 24, 32, 48, 64, 128, 256)

def make_ico(svg: Path, output: Path) -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance() or QGuiApplication([])
    renderer = QSvgRenderer(str(svg))
    if not renderer.isValid():
        raise ValueError("SVG da Fênix invalido")
    images = []
    for size in SIZES:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not pixmap.save(buffer, "PNG"):
            raise RuntimeError("Falha ao gerar PNG para ICO")
        images.append(bytes(buffer.data()))
    icon_dir = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + len(images) * 16
    directory = []
    for size, data in zip(SIZES, images):
        directory.append(struct.pack("<BBBBHHII", size if size < 256 else 0,
                                     size if size < 256 else 0, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(icon_dir + b"".join(directory) + b"".join(images))
    assert output.read_bytes()[:4] == b"\0\0\1\0"

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    make_ico(root / "assets/icons/callas.svg", root / "assets/icons/callas.ico")
