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
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
os.environ['CALLAS_SMOKE'] = '1'
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDialog, QFrame, QLabel, QProgressBar, QPushButton, QSpinBox, QSplitter
from app import MainWindow, STYLE
import windows_actions

app = QApplication(sys.argv)
app.setStyleSheet(STYLE)
win = MainWindow()
win.program_updates_checked = True  # Evita concorrência com a verificação simulada mais abaixo.
win.show()
app.processEvents()
assert win.isVisible()
assert win.minimumWidth() <= 810
assert len(win.pages) == 18, len(win.pages)
assert not win.findChildren(QSplitter)
home = win.pages["home"]
storage = home.findChild(QFrame, "Hero").findChild(QProgressBar)
disk_usage = SimpleNamespace(total=100 * 1024**3, free=60 * 1024**3)
with patch("app.shutil.disk_usage", return_value=disk_usage):
    win.refresh_system_metrics()
    assert storage.isVisible() and storage.value() == 40
with patch("app.shutil.disk_usage", side_effect=OSError):
    win.refresh_system_metrics()
    assert storage.isHidden()
win.refresh_system_metrics()
assert storage.isVisible()

# Navegação por botões laterais e novo percurso depois de retroceder.
win.goto("clean")
win.goto("gamer")
win.goto("gamer")
win.goto("repair")
QTest.mouseClick(win.pages["repair"].viewport(), Qt.MouseButton.BackButton)
assert win.stack.currentWidget() is win.pages["gamer"]
QTest.mouseClick(win.pages["gamer"].viewport(), Qt.MouseButton.ForwardButton)
assert win.stack.currentWidget() is win.pages["repair"]
QTest.keyClick(win.pages["repair"].viewport(), Qt.Key.Key_Back)
assert win.stack.currentWidget() is win.pages["gamer"]
QTest.keyClick(win.pages["gamer"].viewport(), Qt.Key.Key_Forward)
assert win.stack.currentWidget() is win.pages["repair"]
QTest.mouseClick(win.pages["repair"].viewport(), Qt.MouseButton.BackButton)
QTest.mouseClick(win.pages["gamer"].viewport(), Qt.MouseButton.BackButton)
assert win.stack.currentWidget() is win.pages["clean"]
win.goto("shutdown")
QTest.mouseClick(win.pages["shutdown"].viewport(), Qt.MouseButton.ForwardButton)
assert win.stack.currentWidget() is win.pages["shutdown"]

# Cada aba interna pode ser aberta no Início, e a navegação permanece na mesma janela.
win.goto("home")
shortcuts = {button.accessibleName() or button.text(): button
             for button in win.pages["home"].findChildren(QPushButton)}
home_button = next(button for button in win.findChildren(QPushButton) if button.text() == "Início")
assert home_button.isHidden()
for title, route in (
    ("Programas", "programs"), ("Limpeza Total", "clean"), ("Modo Gamer", "gamer"),
    ("Reparar Windows", "repair"), ("Drivers", "drivers"), ("Rede e DNS", "network"),
    ("Windows Update", "windows_update"), ("Privacidade", "privacy"), ("Desligamento", "shutdown"),
    ("Microsoft Edge", "edge"), ("Menu clássico", "classic"), ("WinUtil", "winutil"),
    ("Ponto de restauração", "restore_point"), ("Restaurar padrões", "restore"),
    ("Atualizações do Callas", "updates"), ("Registros", "logs"), ("Sobre", "about"),
):
    assert not shortcuts[title].isHidden(), title
    button = shortcuts[title]
    QTest.mouseClick(button, Qt.MouseButton.LeftButton, pos=QPoint(20, 14))
    app.processEvents()
    assert win.stack.currentWidget() is win.pages[route], (title, route)
    assert home_button.isVisible()
    home_button.click()
    assert win.stack.currentWidget() is win.pages["home"] and home_button.isHidden()
with patch("app.os", SimpleNamespace(name="nt", startfile=Mock())) as windows:
    shortcuts["Inicialização"].click()
    windows.startfile.assert_called_once_with("ms-settings:startupapps")
    assert win.stack.currentWidget() is home
assert shortcuts["Programas"].mapTo(home.viewport(), QPoint()).x() < (
    shortcuts["Limpeza Total"].mapTo(home.viewport(), QPoint()).x()
)
assert shortcuts["Atualizações do Callas"].x() < shortcuts["Registros"].x() < shortcuts["Sobre"].x()
home.setFocus()
for title in (
    "Programas", "Limpeza Total", "Modo Gamer", "Reparar Windows", "Drivers",
    "Rede e DNS", "Windows Update", "Inicialização", "Privacidade", "Desligamento",
    "Microsoft Edge", "Menu clássico", "WinUtil", "Ponto de restauração", "Restaurar padrões",
    "Atualizações do Callas", "Registros", "Sobre",
):
    QTest.keyClick(app.focusWidget(), Qt.Key.Key_Tab)
    assert app.focusWidget() is shortcuts[title], (title, app.focusWidget())

# Com a janela reduzida, os atalhos continuam no viewport e a Fênix segue no painel.
win.resize(810, 570)
QTest.qWait(100)  # O Qt recalcula o viewport depois de reorganizar as grades.
assert win.hero_phoenix.isVisible()
for button in shortcuts.values():
    left = button.mapTo(home.viewport(), QPoint()).x()
    right = left + button.width()
    assert 0 <= left < right <= home.viewport().width(), (
        button.accessibleName() or button.text(), left, right,
        win.width(), home.viewport().width(), home.widget().width(), home.widget().minimumSizeHint().width(),
        win._home_profile, win.home_quick_grid.minimumSize(), win.home_tools_grid.minimumSize(),
        [item.minimumSizeHint().width() for item in win.home_tool_buttons],
    )
assert home.verticalScrollBar().maximum() > 0

win.goto("about")
app.processEvents()
about_buttons = win.pages["about"].findChildren(QPushButton)
repo_button = next(button for button in about_buttons if button.text() == "Abrir repositório")
assert repo_button.height() <= 36 and repo_button.width() < 200, repo_button.size()
with patch("app.webbrowser.open") as browser:
    repo_button.click()
    browser.assert_called_once_with("https://github.com/Callas157/Callas-Optimizer-Windows")
setup_button = next(button for button in about_buttons if button.text() == "Obter instalador oficial")
with patch("app.webbrowser.open") as browser:
    setup_button.click()
    browser.assert_called_once_with("https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest")

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
    assert primary.text() == "Abrir" and bar.isHidden() and bar.value() == 100 and not bar.running
    win.program_updates_done(set(), False)
    assert not upgrade.isHidden() and upgrade.text() == "Atualizar"
    assert all(not control[1].isHidden() for control in win.program_controls.values())
    assert primary.size() == upgrade.size() and primary.width() > 2 * primary.height()
    assert primary.y() == upgrade.y() and primary.x() < upgrade.x()
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
        assert bar.isHidden() and bar.value() == 100 and primary.text() == "Abrir"
for route in ("home", "clean", "gamer", "repair", "programs", "drivers", "updates"):
    win.goto(route)
    assert win.stack.currentWidget() is win.pages[route]

# As ferramentas e a Central usam a largura disponível na janela.
win.resize(1450, 850)
for route, titles in (("repair", ("Reparar imagem com DISM", "Reparar arquivos com SFC", "Examinar disco do sistema")),
                      ("restore", ("Restaurar ajustes do Registro", "Restaurar serviços", "Restaurar ajustes salvos"))):
    win.goto(route)
    app.processEvents()
    page = win.pages[route]
    headings = {item.text(): item for item in page.findChildren(QLabel)}
    positions = [headings[title].mapTo(page.viewport(), QPoint()) for title in titles]
    assert len({point.y() for point in positions}) == 1, (route, positions)
    assert positions[0].x() < positions[1].x() < positions[2].x(), (route, positions)
win.goto("programs")
app.processEvents()
first, second, third, fourth = win.all_program_cards[:4]
assert first.y() == second.y() == third.y() < fourth.y()
normal_card_width = first.width()
win.resize(1920, 850)
app.processEvents()
viewport = win.pages["programs"].viewport()
left = first.mapTo(viewport, QPoint()).x()
right = viewport.width() - third.mapTo(viewport, third.rect().topRight()).x() - 1
heading = win.pages["programs"].findChild(QLabel, "Title")
assert abs(left - right) <= 3 and left > 22, (left, right)
assert heading.mapTo(viewport, QPoint()).x() == left
assert first.y() == second.y() == third.y() < fourth.y()
assert first.width() == normal_card_width <= 395

win.goto("repair")
win.resize(810, 680)
win.goto("programs")
app.processEvents()
assert first.mapTo(win.pages["programs"].viewport(), QPoint()).y() < 260
assert first.y() == second.y() < third.y() == fourth.y()
assert first.height() >= 100, first.size()
for card in win.all_program_cards:
    for item in card.findChildren(QLabel):
        if not item.isHidden():
            assert item.height() >= item.heightForWidth(item.width()), (item.text(), item.size())
    for button in card.findChildren(QPushButton):
        if not button.isHidden():
            assert card.rect().contains(button.mapTo(card, QPoint()) + button.rect().bottomRight())
status = win.program_controls["brave"][3]
status.setText(r"[WinError 5] Acesso negado: C:\Users\very.long.enterprise.username.fl.name\AppData\Local\CallasTeck\Downloads\brave-E7J5wxxG\BraveBrowserStandaloneSetup.exe")
status.show()
app.processEvents()
app.processEvents()
viewport = win.pages["programs"].viewport()
assert first.mapTo(viewport, first.rect().topRight()).x() < viewport.width()
assert first.y() == second.y() < third.y()
status.hide()
win.goto("winutil")
app.processEvents()
execute = next(button for button in win.pages["winutil"].findChildren(QPushButton)
               if "Executar" in button.text())
assert execute.height() <= 36 and execute.width() <= 145
winutil_card = win.native_controls["winutil_open"].widget
assert winutil_card.width() <= 410 and winutil_card.width() >= 2 * winutil_card.height(), winutil_card.size()
viewport = win.pages["winutil"].viewport()
card_bottom = winutil_card.mapTo(viewport, winutil_card.rect().bottomLeft())
logs = next(button for button in win.pages["winutil"].findChildren(QPushButton)
            if button.text() == "Ver registros")
assert card_bottom.x() <= 24
assert 0 < logs.mapTo(viewport, QPoint()).y() - card_bottom.y() <= 25
win.resize(1450, 850)
win.goto("drivers")
app.processEvents()
driver_cards = win.pages["drivers"].findChildren(QFrame, "Card")
assert len(driver_cards) == 2 and all(card.width() >= 2 * card.height() for card in driver_cards)

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
win.goto("programs")
win.resize(810, 610)
app.processEvents()
win.showMaximized()
app.processEvents()
assert win.isMaximized(), 'Nao maximizou'
viewport = win.pages["programs"].viewport()
assert first.mapTo(viewport, first.rect().topRight()).x() < viewport.width()
if viewport.width() >= 900:
    assert first.y() == second.y() == third.y() < fourth.y()
    left = first.mapTo(viewport, QPoint()).x()
    right = viewport.width() - third.mapTo(viewport, third.rect().topRight()).x() - 1
    assert abs(left - right) <= 3
win.showNormal()
app.processEvents()
assert first.y() == second.y() < third.y()
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
        card = worker.native_controls['repair_disk']
        run, progress, stack, status = card.button, card.progress, card.execution, card.status
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
        assert stack.currentWidget() is run and run.isEnabled()
        run.click()
        worker.native_report.with_suffix('.progress').write_text('{"percent": 30}', encoding='utf-8')
        worker.poll_native_action()
        worker.poll_native_action()
        assert worker.native_timer is None and progress.value() == 30 and not progress.running
        assert '7' in status.text() and stack.currentWidget() is run
        warning.assert_not_called()
        info.assert_not_called()

    backup_path = local / "actions_backup.json"
    game_mode = "CU|Software\\Microsoft\\GameBar|AutoGameModeEnabled"
    with patch("windows_actions.BACKUP", backup_path), patch("app.ACTION_HOME", local), \
            patch("app.os", SimpleNamespace(name="nt")), patch("app.confirmar", return_value=True), \
            patch("app.subprocess.Popen") as spawn:
        worker.goto("gamer")
        card = worker.native_controls["gamer_on"]
        assert card.button.text() == "Aplicar"
        assert "gamer_off" not in worker.native_controls
        spawn.return_value.poll.return_value = 0
        card.button.click()
        assert worker.native_code == "gamer_on" and card.execution.currentWidget() is card.progress
        backup_path.write_text(json.dumps({"reg": {game_mode: {"found": False}}}), encoding="utf-8")
        worker.native_report.write_text('{"ok": true, "message": "Salvo."}', encoding="utf-8")
        worker.poll_native_action()
        assert card.button.text() == "Reverter" and card.execution.currentWidget() is card.button

        with patch("app.os", os):
            reopened = MainWindow()
        assert reopened.native_controls["gamer_on"].button.text() == "Reverter"
        reopened.close()
        card.button.click()
        assert worker.native_code == "gamer_off" and card.execution.currentWidget() is card.progress
        worker.native_report.write_text('{"ok": false, "message": "Falhou."}', encoding="utf-8")
        worker.poll_native_action()
        assert card.button.text() == "Reverter" and card.execution.currentWidget() is card.button
        card.button.click()
        backup_path.unlink()
        worker.native_report.write_text('{"ok": true, "message": "Restaurado."}', encoding="utf-8")
        worker.poll_native_action()
        assert card.button.text() == "Aplicar" and card.execution.currentWidget() is card.button

    with patch("app.ACTION_HOME", local), patch("app.os", SimpleNamespace(name="nt")), \
            patch("app.confirmar", return_value=True), patch("app.edge_installed") as edge_installed, \
            patch("app.ElevatedAction") as elevate, patch("app.subprocess.Popen") as spawn:
        edge_installed.return_value = True
        elevate.return_value.poll.return_value = 0
        spawn.return_value.poll.return_value = 0
        worker.goto("edge")
        card = worker.native_controls["edge_uninstall"]
        assert card.button.text() == "Remover"
        card.button.click()
        assert worker.native_code == "edge_uninstall"
        edge_installed.return_value = False
        worker.native_report.write_text('{"ok": true, "message": "Removido."}', encoding="utf-8")
        worker.poll_native_action()
        assert card.button.text() == "Restaurar" and card.execution.currentWidget() is card.button
        card.button.click()
        assert worker.native_code == "edge_restore"
        edge_installed.return_value = True
        worker.native_report.write_text('{"ok": true, "message": "Restaurado."}', encoding="utf-8")
        worker.poll_native_action()
        assert card.button.text() == "Remover" and card.execution.currentWidget() is card.button

    provider = {}
    with patch("app.dns_provider_status", side_effect=lambda: dict(provider)), \
            patch("app.ACTION_HOME", local), patch("app.os", SimpleNamespace(name="nt")), \
            patch("app.confirmar", return_value=True), patch("app.ElevatedAction") as elevate:
        cloudflare = worker.native_controls["dns_cloudflare"]
        google = worker.native_controls["dns_google"]

        def wait_dns():
            deadline = time.monotonic() + 2
            while (not cloudflare.button.isEnabled() or not google.button.isEnabled()) and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(0.01)
            assert cloudflare.button.isEnabled() and google.button.isEnabled()

        def finish_dns(selected):
            provider.clear()
            if selected:
                provider[selected] = False
            worker.native_report.write_text('{"ok": true, "message": "DNS confirmado."}', encoding="utf-8")
            worker.poll_native_action()
            wait_dns()

        elevate.return_value.poll.return_value = 0
        worker.goto("network")
        wait_dns()
        assert "dns_auto" not in worker.native_controls
        assert cloudflare.button.text() == google.button.text() == "Aplicar"
        cloudflare.button.click()
        assert worker.native_code == "dns_cloudflare"
        assert cloudflare.execution.currentWidget() is cloudflare.progress
        finish_dns("dns_cloudflare")
        assert cloudflare.button.text() == "Reverter"
        assert cloudflare.execution.currentWidget() is cloudflare.button
        assert google.button.text() == "Aplicar"
        google.button.click()
        assert worker.native_code == "dns_google"
        finish_dns("dns_google")
        assert cloudflare.button.text() == "Aplicar"
        assert google.button.text() == "Reverter"
        google.button.click()
        assert worker.native_code == "dns_google_auto"
        finish_dns(None)
        assert cloudflare.button.text() == google.button.text() == "Aplicar"
        assert google.status.text().startswith("Concluído.")
        worker.update_dns_actions(worker.dns_status_request, {"dns_cloudflare": True, "dns_google": True})
        assert cloudflare.button.text() == google.button.text() == "Reverter"
        assert not worker.dns_apply_buttons["dns_google"].isHidden()
        worker.dns_apply_buttons["dns_google"].click()
        assert worker.native_code == "dns_google"
        finish_dns("dns_google")
        assert worker.dns_apply_buttons["dns_google"].isHidden()
        assert cloudflare.status.isHidden()
        worker.update_dns_actions(worker.dns_status_request, None)
        assert not google.button.isEnabled()
        assert "Não foi possível consultar o DNS" in worker.status_label.text()

    deadline = [None]
    with patch("windows_actions._read_shutdown_deadline", side_effect=lambda: deadline[0]), \
            patch("windows_actions._write_shutdown_deadline", side_effect=lambda value: deadline.__setitem__(0, value)), \
            patch("windows_actions.cmd", return_value="OK"), \
            patch("app.ACTION_HOME", local), patch("app.confirmar", return_value=True), \
            patch("app.subprocess.Popen") as spawn:
        worker.goto("shutdown")
        timer_card = worker.native_controls["shutdown_custom"]
        assert timer_card.button.text() == "Configurar"
        seen = {}

        def choose_time():
            dialog = app.activeModalWidget()
            if not isinstance(dialog, QDialog):
                worker.close()
                return
            picker = dialog.findChild(QSpinBox)
            controls = {button.text(): button for button in dialog.findChildren(QPushButton)}
            if picker is None or not {"60 min", "Agendar"} <= controls.keys():
                dialog.reject()
                return
            seen["centered"] = (dialog.geometry().center() - worker.frameGeometry().center()).manhattanLength() < 20
            controls["60 min"].click()
            seen["preset"] = picker.value()
            picker.setValue(35)
            QTest.keyClick(picker, Qt.Key.Key_Return)
            if dialog.isVisible():
                seen["enter_submitted"] = False
                dialog.reject()
            else:
                seen["enter_submitted"] = True

        spawn.return_value.poll.return_value = 0
        with patch("app.os", SimpleNamespace(name="nt")):
            QTimer.singleShot(0, choose_time)
            timer_card.button.click()
        assert seen == {"centered": True, "preset": 60, "enter_submitted": True}, seen
        assert spawn.call_args.args[0][-2:] == ["--shutdown-minutes", "35"]
        assert timer_card.execution.currentWidget() is timer_card.progress

        windows_actions.shutdown(35)
        worker.native_report.write_text('{"ok": true, "message": "Agendado."}', encoding="utf-8")
        worker.poll_native_action()
        assert timer_card.title.text() == "Desligando em 35 minutos"
        assert timer_card.button.text() == "Reagendar"

        deadline[0] -= 30 * 60_000_000_000
        restored = MainWindow()
        restored.goto("shutdown")
        restored_card = restored.native_controls["shutdown_custom"]
        assert restored_card.title.text() == "Desligando em 5 minutos"
        deadline[0] -= 60_000_000_000
        restored.shutdown_countdown.timeout.emit()
        assert restored_card.title.text() == "Desligando em 4 minutos"
        with patch("app.os", SimpleNamespace(name="nt")):
            restored.native_controls["shutdown_cancel"].button.click()
        windows_actions.shutdown(None)
        restored.native_report.write_text('{"ok": true, "message": "Cancelado."}', encoding="utf-8")
        restored.poll_native_action()
        assert restored_card.title.text() == "Desligamento personalizado"
        assert restored_card.button.text() == "Configurar"
        restored.close()

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
