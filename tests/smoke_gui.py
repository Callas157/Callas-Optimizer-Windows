"""Smoke test real de Qt no runner Windows com display offscreen."""
import os
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
from app import MainWindow, STYLE

app = QApplication(sys.argv)
app.setStyleSheet(STYLE)
win = MainWindow()
win.show()
app.processEvents()
assert win.isVisible()
assert win.minimumWidth() <= 810
assert len(win.pages) == 17, len(win.pages)
win.goto('clean')
assert win.stack.currentWidget() is win.pages['clean']
win.goto('programs')
assert win.stack.currentWidget() is win.pages['programs']
assert len(win.all_program_cards) == 5
assert all(not card is None for card in win.all_program_cards)
win.resize(930, 610)
app.processEvents()
win.showMaximized()
app.processEvents()
assert win.isMaximized(), 'Nao maximizou'
win.close()
print('Navegacao, redimensionamento, maximizar e icones Qt: OK')
