"""Smoke test real de Qt no runner Windows com display offscreen."""
import os
import sys
from pathlib import Path
from unittest.mock import patch
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication, QPushButton
from app import MainWindow, STYLE

app = QApplication(sys.argv)
app.setStyleSheet(STYLE)
win = MainWindow()
win.show()
app.processEvents()
assert win.isVisible()
assert win.minimumWidth() <= 810
assert len(win.pages) == 18, len(win.pages)
assert len(win.home_tiles) == 6
assert len(win.home_panels) == 5
assert hasattr(win, "home_detail_grid")
assert callable(win.open_windows_settings)

# Testar clique real nos cartões da tela inicial sem nova janela.
win.goto('home')
quick = win.pages['home'].findChildren(QPushButton)
for text, route in (("Clean", "clean"), ("Boost", "gamer"), ("Repair", "repair"),
                    ("Apps", "programs"), ("Drivers", "drivers"), ("Atualizar", "updates")):
    win.goto('home')
    match = next((b for b in quick if text in b.text()), None)
    assert match is not None, text
    match.click()
    app.processEvents()
    assert win.stack.currentWidget() is win.pages[route], (text, route)
win.goto('clean')
assert win.stack.currentWidget() is win.pages['clean']
win.goto('programs')
assert win.stack.currentWidget() is win.pages['programs']
assert len(win.all_program_cards) == 12
assert all(not card is None for card in win.all_program_cards)
assert win.chatgpt_card in win.all_program_cards
assert win.codex_card in win.all_program_cards
for card in (win.discord_card, win.steam_card, win.epic_card, win.wise_card, win.virtualbox_card):
    assert card in win.all_program_cards
for key in ("steam", "discord", "epic", "medal", "lghub", "wise", "virtualbox"):
    assert (root / "assets" / "icons" / f"{key}.png").is_file()
    assert not win.program_icons[key].pixmap().isNull()
with patch("app.installed_program", return_value=None):
    win.refresh_program_cards()
    primary, upgrade, bar, status = win.program_controls["discord"]
    assert primary.text() == "Instalar"
    win.installing_program = "discord"
    win.show_program_progress("Baixando…", 42)
    assert primary.isHidden() and not bar.isHidden() and bar.value() == 42
    assert status.text() == "Baixando…"
with patch("app.installed_program", return_value=Path("Discord.exe")):
    win.extra_installer_done(True, "", "discord")
    assert primary.text() == "Abrir" and bar.isHidden()
    win.program_updates_done({"discord"}, False)
    assert not upgrade.isHidden() and upgrade.text() == "Atualizar"
medal = Path(r"C:\Medal\current\Medal.exe")
with patch("app.installed_program", return_value=medal), patch("app.open_program") as launch:
    win.refresh_program_cards()
    primary, _, _, _ = win.program_controls["medal"]
    assert primary.text() == "Abrir"
    primary.click()
    launch.assert_called_once_with(medal)
win.installing_program = "chatgpt"
win.show_program_progress("Baixando…", 38)
for key in ("chatgpt", "codex"):
    primary, _, bar, status = win.program_controls[key]
    assert primary.isHidden() and not bar.isHidden() and bar.value() == 38
    assert status.text() == "Baixando…"
with patch("app.installed_program", return_value="shell:AppsFolder\\ChatGPT!App"):
    win.extra_installer_done(True, "", "chatgpt")
    for key in ("chatgpt", "codex"):
        primary, _, bar, _ = win.program_controls[key]
        assert bar.isHidden() and primary.text() == "Abrir"
for route in ("home", "clean", "gamer", "repair", "programs", "drivers", "updates"):
    win.goto(route)
    assert win.stack.currentWidget() is win.pages[route]
win.resize(930, 610)
app.processEvents()
win.showMaximized()
app.processEvents()
assert win.isMaximized(), 'Nao maximizou'
win.close()
print('Navegacao, redimensionamento, maximizar e icones Qt: OK')
