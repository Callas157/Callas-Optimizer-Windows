"""Barra de tarefa com porcentagem medida e animação de atividade."""
from PySide6.QtCore import QAbstractAnimation, QRectF, Qt, QVariantAnimation, Slot
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QProgressBar


class TaskProgressBar(QProgressBar):
    def __init__(self, name: str):
        super().__init__()
        self.setAccessibleName(name)
        self.setMinimumHeight(40)
        self.setRange(0, 100)
        self.setValue(0)
        self._failed = False
        self._shine = QVariantAnimation(self)
        self._shine.setStartValue(0.0)
        self._shine.setEndValue(1.0)
        self._shine.setDuration(1450)
        self._shine.setLoopCount(-1)
        self._shine.valueChanged.connect(lambda _: self.update())

    @property
    def running(self) -> bool:
        return self._shine.state() == QAbstractAnimation.State.Running

    def begin(self):
        self._failed = False
        self.setValue(0)
        self._shine.start()
        self.update()

    @Slot(int)
    def advance(self, percent: int):
        if self.running and 0 <= percent <= 100:
            self.setValue(min(percent, 99))

    def finish(self, success: bool):
        self._shine.stop()
        self._failed = not success
        if success:
            self.setValue(100)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        outline = QPainterPath()
        outline.addRoundedRect(track, 10, 10)
        painter.fillPath(outline, QColor("#101631"))
        painter.save()
        painter.setClipPath(outline)

        fill = QLinearGradient(track.topLeft(), track.topRight())
        fill.setColorAt(0, QColor("#a02bdf"))
        fill.setColorAt(0.58, QColor("#6549f7"))
        fill.setColorAt(1, QColor("#0a91d9"))
        done = QRectF(track)
        done.setWidth(track.width() * self.value() / 100)
        painter.fillRect(done, fill)

        if self.running:
            shimmer_width = max(56, track.width() * 0.36)
            left = track.left() - shimmer_width + (track.width() + shimmer_width) * self._shine.currentValue()
            shimmer = QLinearGradient(left, 0, left + shimmer_width, 0)
            shimmer.setColorAt(0, QColor(117, 202, 255, 0))
            shimmer.setColorAt(0.52, QColor(117, 202, 255, 95))
            shimmer.setColorAt(1, QColor(117, 202, 255, 0))
            painter.fillRect(track, shimmer)

        painter.restore()
        painter.setPen(QPen(QColor("#bf828b" if self._failed else "#7965ae")))
        painter.drawPath(outline)

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        text = self.text()
        badge_width = painter.fontMetrics().horizontalAdvance(text) + 20
        badge_height = painter.fontMetrics().height() + 4
        badge = QRectF(
            track.center().x() - badge_width / 2, track.center().y() - badge_height / 2,
            badge_width, badge_height,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(10, 14, 42, 230))
        painter.drawRoundedRect(badge, 6, 6)
        painter.setPen(QColor("#f8f8ff"))
        painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, text)
