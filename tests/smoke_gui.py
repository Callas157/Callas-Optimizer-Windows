"""Smoke test real de Qt no runner Windows com display offscreen."""
import os
import json
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['CALLAS_SMOKE'] = '1'
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
assert win.vm_template_button.text() == "PREPARAR / AJUSTAR 2 VMS"
assert callable(win.prepare_virtualbox_templates)
assert all(not card is None for card in win.all_program_cards)
assert win.chatgpt_card in win.all_program_cards
assert win.codex_card in win.all_program_cards
for card in (win.discord_card, win.steam_card, win.epic_card, win.wise_card, win.virtualbox_card):
    assert card in win.all_program_cards
for key in ("steam", "discord", "epic", "medal", "lghub", "wise"):
    assert (root / "assets" / "icons" / f"{key}.png").is_file()
    assert not win.program_icons[key].pixmap().isNull()
# VirtualBox usa um SVG próprio de fallback; quando instalado usa o ícone do EXE.
assert (root / "assets" / "icons" / "virtualbox.svg").is_file()
assert not win.program_icons["virtualbox"].pixmap().isNull()
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
    assert primary.text() == "Abrir" and not bar.isHidden() and bar.value() == 100 and not bar.running
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
        assert not bar.isHidden() and bar.value() == 100 and primary.text() == "Abrir"
for route in ("home", "clean", "gamer", "repair", "programs", "drivers", "updates"):
    win.goto(route)
    assert win.stack.currentWidget() is win.pages[route]
for route, button in win.nav_buttons.items():
    button.click()
    assert win.stack.currentWidget() is win.pages[route], route

assert not win.clean_nvidia.isChecked()
with tempfile.TemporaryDirectory() as directory:
    local = Path(directory).resolve()
    dxcache = local / "NVIDIA" / "DXCache"
    dxcache.mkdir(parents=True)
    shader = dxcache / "test.shader"
    shader.write_bytes(b"test")
    icons = local / "IconCache.db"
    icons.write_bytes(b"test")
    win.goto("clean")
    win.clean_user.setChecked(False)
    win.clean_nvidia.setChecked(True)
    win.clean_icons.setChecked(True)
    win.clean_recycle.setChecked(True)
    with patch.dict(os.environ, {"LOCALAPPDATA": str(local)}), patch("app.confirmar", return_value=True):
        with patch("app.empty_recycle_bin", return_value="já vazia"), patch("cleaner.refresh_shell_icons"):
            win.clean_start.click()
            deadline = time.monotonic() + 10
            while win.cleaner is not None and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(.01)
    assert win.cleaner is None and win.clean_start.isEnabled()
    assert win.clean_progress.value() == 100 and not win.clean_progress.running
    output = win.clean_output.toPlainText()
    assert "Lixeira: já vazia" in output and "Cache de ícones: 1 removido" in output
    assert not shader.exists() and not icons.exists() and dxcache.is_dir()
win.resize(930, 610)
app.processEvents()
win.showMaximized()
app.processEvents()
assert win.isMaximized(), 'Nao maximizou'
win.close()
print('Navegacao, redimensionamento, maximizar e icones Qt: OK')

# As falhas dos trabalhadores e os conflitos com o atualizador devem aparecer
# na interface sem executar ações do Windows no computador do teste.
worker = MainWindow()
with tempfile.TemporaryDirectory() as directory:
    local = Path(directory).resolve()
    with patch('app.ACTION_HOME', local), patch('app.os', SimpleNamespace(name='nt')), \
            patch('app.confirmar', return_value=True), patch('app.ElevatedAction') as elevate, \
            patch('app.QMessageBox.warning') as warning, patch('app.QMessageBox.information') as info:
        run, progress, stack, status, repeat = worker.native_controls['repair_disk']
        worker.goto('repair')
        worker.show()
        elevate.return_value.poll.side_effect = [None, None, 0, None, 7]
        run.click()
        app.processEvents()
        assert stack.currentWidget() is progress and progress.value() == 0 and progress.running
        previous_frame = progress.grab().toImage()
        deadline = time.monotonic() + .09
        while time.monotonic() < deadline:
            app.processEvents()
            time.sleep(.01)
        assert progress.grab().toImage() != previous_frame
        intermediate = worker.native_report.with_suffix('.progress')
        intermediate.write_text('{"percent": 62}', encoding='utf-8')
        worker.poll_native_action()
        assert progress.value() == 62
        intermediate.write_text('{parcial', encoding='utf-8')
        worker.poll_native_action()
        assert progress.value() == 62 and progress.running
        outcome = {"ok": True, "message": "O Windows verificou o sistema de arquivos e não encontrou problemas.\n" + "Registro de arquivo\n" * 100}
        worker.native_report.write_text(json.dumps(outcome, ensure_ascii=False), encoding='utf-8')
        worker.poll_native_action()
        assert worker.native_timer is None and not intermediate.exists()
        assert progress.value() == 100 and not progress.running
        assert 'não encontrou problemas' in status.text() and len(status.text()) < 450
        assert not repeat.isHidden()
        repeat.click()
        worker.native_report.with_suffix('.progress').write_text('{"percent": 30}', encoding='utf-8')
        worker.poll_native_action()
        worker.poll_native_action()
        assert worker.native_timer is None and progress.value() == 30 and not progress.running
        assert '7' in status.text()
        warning.assert_not_called()
        info.assert_not_called()

    worker.update_mode = 'install'
    worker.update_timer = Mock()
    worker.update_status = local / 'check.status'
    worker.update_progress.begin()
    worker.update_status.write_text('PROGRESS|41|Baixando o instalador...', encoding='ascii')
    worker.updater_process = Mock()
    worker.updater_process.poll.return_value = None
    worker.poll_update()
    assert worker.update_progress.value() == 41 and worker.update_progress.running
    assert 'Baixando' in worker.update_note.text()
    worker.update_status.write_text('CURRENT', encoding='ascii')
    worker.updater_process = Mock()
    worker.updater_process.poll.return_value = 0
    with patch('app.QMessageBox.warning') as warning:
        worker.poll_update()
        warning.assert_not_called()
    assert worker.update_mode == ''
    assert worker.update_progress.value() == 100 and not worker.update_progress.running
    assert worker.update_note.text() == 'Você está na versão mais recente.'

    worker.update_mode = 'check'
    worker.update_timer = Mock()
    worker.update_progress.begin()
    worker.update_status.write_text('PROGRESS|0|Consultando o GitHub...', encoding='ascii')
    worker.updater_process = Mock()

    def finish_update_check():
        worker.update_status.write_text('AVAILABLE|v99.0.0', encoding='ascii')
        return 0

    worker.updater_process.poll.side_effect = finish_update_check
    with patch('app.confirmar', return_value=False) as offer_update:
        worker.poll_update()
        offer_update.assert_called_once()
    assert worker.update_note.text() == 'Disponível: v99.0.0'

worker.vm_template_thread = Mock()
worker.vm_template_thread.isRunning.return_value = True
with patch('app.QMessageBox.information') as info:
    worker.install_update()
    info.assert_not_called()
assert 'tarefa em andamento' in worker.update_note.text()
worker.vm_template_thread = None
worker.update_mode = 'install'
with patch('app.get_vboxmanage') as get_vbox:
    worker.prepare_virtualbox_templates()
    get_vbox.assert_not_called()
worker.update_mode = ''
def confirm_while_update_starts(*args):
    worker.update_mode = 'install'
    return True

with patch('app.confirmar', side_effect=confirm_while_update_starts), \
        patch('app.known_temp_folders', return_value=[Path(tempfile.gettempdir())]), \
        patch('app.CleanerThread') as start:
    worker.start_clean()
    start.assert_not_called()
worker.update_mode = ''
worker.close()
print('Execução e relato de tarefas, convivência com a atualização: OK')
