"""Gera ICO multirresolucao com a imagem PNG da Fênix aprovada."""
from __future__ import annotations

import os
from pathlib import Path
import struct

from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QPixmap

SIZES = (16, 24, 32, 48, 64, 128, 256)


def make_ico(source: Path, output: Path) -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance() or QGuiApplication([])
    approved = QPixmap(str(source))
    if approved.isNull():
        raise ValueError("PNG da Fênix inválido ou ausente")
    images = []
    for size in SIZES:
        pixmap = approved.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not pixmap.save(buffer, "PNG"):
            raise RuntimeError("Falha ao gerar PNG para ICO")
        images.append(bytes(buffer.data()))
    icon_dir = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + len(images) * 16
    entries = []
    for size, data in zip(SIZES, images):
        entries.append(struct.pack("<BBBBHHII", size if size < 256 else 0,
                                   size if size < 256 else 0, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(icon_dir + b"".join(entries) + b"".join(images))
    assert output.read_bytes()[:4] == b"\0\0\1\0"


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    make_ico(root / "assets/icons/phoenix-approved.png", root / "assets/icons/callas.ico")
