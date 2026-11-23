"""Testes das funções Python Windows (não realizam mutações no runner)."""
import ast
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
class NativeActionContracts(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows launcher required")
    def test_winutil_action_opens_the_tool_instead_of_the_browser(self):
        sys.path.insert(0, str(ROOT / "src"))
        import windows_actions as actions
        self.assertTrue(actions.ACTIONS["winutil_open"]["admin"])
        with patch.object(actions, "admin", return_value=True), patch.object(actions, "open_winutil") as launch:
            with patch.object(actions, "LOG") as log, patch.object(actions, "HOME"):
                launch.return_value = "WinUtil aberto."
                actions.execute("winutil_open")
                log.open.assert_called_once()
        launch.assert_called_once_with()

    @unittest.skipUnless(sys.platform == "win32", "Windows launcher required")
    def test_winutil_rejects_a_changed_release_before_starting_powershell(self):
        sys.path.insert(0, str(ROOT / "src"))
        import windows_actions as actions
        with patch.object(actions, "official_https_opener") as opener, patch.object(actions.subprocess, "Popen") as launch:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.read.return_value = b"an unexpected payload"
            with self.assertRaisesRegex(RuntimeError, "SHA-256"):
                actions.open_winutil()
        launch.assert_not_called()

    @unittest.skipUnless(sys.platform == "win32", "Windows registry module required")
    def test_restore_ignores_registry_entries_outside_product_settings(self):
        sys.path.insert(0, str(ROOT / "src"))
        import windows_actions
        entry = {"hive": "LM", "path": r"SOFTWARE\Other", "name": "Setting",
                 "found": True, "value": 1, "type": windows_actions.winreg.REG_DWORD}
        backup = {"reg": {r"LM|SOFTWARE\Other|Setting": entry}}
        with patch.object(windows_actions, "load", return_value=backup):
            with patch.object(windows_actions.winreg, "CreateKeyEx") as write:
                windows_actions.restore_reg()
        write.assert_not_called()

    def test_catalogue(self):
        s=(ROOT/'src/windows_actions.py').read_text(encoding='utf-8')
        module = ast.parse(s)
        for route in ('gamer','edge','windows_update','network','privacy','repair',
                      'classic','shutdown','winutil','restore_point','restore'):
            self.assertIn(f'"{route}"',s)
        self.assertIn('shell=False',s)
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == 'worker' for node in module.body))
    def test_gui_no_bat(self):
        s=(ROOT/'src/app.py').read_text(encoding='utf-8')
        ast.parse(s)
        self.assertNotIn('start_admin_bat(',s)
        self.assertNotIn('GUI_Engine.bat',s)
        self.assertIn('self.native_action(code)',s)
        self.assertIn('--callas-task',s)


class MaintenanceRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "src"))
        import windows_actions
        cls.actions = windows_actions

    def execute(self, action_id):
        with patch.object(self.actions, "os", SimpleNamespace(name="nt", environ={"SystemDrive": "D:"})), \
                patch.object(self.actions, "admin", return_value=True), \
                patch.object(self.actions, "LOG"), patch.object(self.actions, "HOME"):
            return self.actions.execute(action_id)

    def test_disk_scan_passes_system_volume_without_a_path(self):
        with patch.object(self.actions, "cmd", return_value="Disco examinado") as command:
            self.assertEqual(self.execute("repair_disk"), "Disco examinado")
        self.assertEqual(command.call_args.args, ("chkdsk.exe", "D:", "/scan"))

    def test_sfc_preserves_portuguese_utf16_output(self):
        text = "A Proteção de Recursos do Windows não encontrou violações."
        result = SimpleNamespace(returncode=0, stdout=text.encode("utf-16le"), stderr=b"")
        with patch.object(self.actions, "os", SimpleNamespace(name="nt")), \
                patch.object(self.actions, "_system_program", return_value=Path("sfc.exe")), \
                patch.object(self.actions.subprocess, "run", return_value=result):
            self.assertEqual(self.actions.cmd("sfc.exe", "/scannow"), text)

    def test_disk_scan_accepts_repaired_errors_but_reports_scan_failure(self):
        for code in (1, 3):
            result = SimpleNamespace(returncode=code, stdout=b"Resultado do exame", stderr=b"")
            with self.subTest(code=code), \
                    patch.object(self.actions.subprocess, "run", return_value=result), \
                    patch.object(self.actions, "_system_program", return_value=Path("chkdsk.exe")):
                if code == 1:
                    self.assertIn("Resultado do exame", self.execute("repair_disk"))
                else:
                    with self.assertRaisesRegex(RuntimeError, "retornou 3"):
                        self.execute("repair_disk")

    def test_restore_point_turns_creation_warning_into_a_failure(self):
        with patch.object(self.actions, "ps", return_value="Ponto criado") as powershell:
            self.execute("restore_point")
        self.assertIn("-WarningAction Stop", powershell.call_args.args[0])

    def test_backup_parse_error_keeps_existing_file(self):
        with TemporaryDirectory() as directory:
            backup = Path(directory) / "actions_backup.json"
            backup.write_text("{corrompido", encoding="utf-8")
            with patch.object(self.actions, "BACKUP", backup):
                with self.assertRaisesRegex(RuntimeError, "backup"):
                    self.actions.load()
            self.assertEqual(backup.read_text(encoding="utf-8"), "{corrompido")

    def test_failed_action_gets_recorded(self):
        with TemporaryDirectory() as directory:
            home = Path(directory)
            log = home / "acoes.log"
            with patch.object(self.actions, "HOME", home), patch.object(self.actions, "LOG", log), \
                    patch.object(self.actions, "os", SimpleNamespace(name="nt")), \
                    patch.object(self.actions, "admin", return_value=True), \
                    patch.object(self.actions, "cmd", side_effect=RuntimeError("DISM indisponível")):
                with self.assertRaisesRegex(RuntimeError, "DISM indisponível"):
                    self.actions.execute("repair_dism")
            self.assertIn("DISM indisponível", log.read_text(encoding="utf-8"))

    def test_hibernation_already_off_does_not_save_an_enabled_state(self):
        backup = {"hiber": False}
        with patch.object(self.actions, "winreg", create=True) as registry, \
                patch.object(self.actions, "load", return_value=backup), \
                patch.object(self.actions, "save") as save, patch.object(self.actions, "cmd") as cmd:
            registry.QueryValueEx.return_value = (0, 4)
            self.assertIn("já estava desativada", self.actions.hibernate(False))
        save.assert_not_called()
        cmd.assert_not_called()

    def test_restore_all_also_restores_hibernation(self):
        with patch.object(self.actions, "load", return_value={"svc": {}, "hiber": True}), \
                patch.object(self.actions, "restore_reg", return_value="Registro"), \
                patch.object(self.actions, "services", return_value="Serviços"), \
                patch.object(self.actions, "energy", return_value="Energia"), \
                patch.object(self.actions, "hibernate", return_value="Hibernação") as hibernate:
            self.assertIn("Hibernação", self.execute("restore_all"))
        hibernate.assert_called_once_with(True)

    def test_service_snapshot_restores_delayed_auto_start_and_old_backups(self):
        backup = {"svc": {"SysMain": 3}}
        with patch.object(self.actions, "winreg", create=True) as registry, \
                patch.object(self.actions, "load", return_value=backup), \
                patch.object(self.actions, "save"), patch.object(self.actions, "cmd") as cmd:
            registry.QueryValueEx.side_effect = lambda key, name: (2 if name == "Start" else 1, 4)
            self.actions.services(("WSearch",), True)
            self.actions.services(("SysMain", "WSearch"), False)
        self.assertIn(("sc.exe", "config", "SysMain", "start=", "demand"),
                      [call.args for call in cmd.call_args_list])
        self.assertEqual(cmd.call_args.args, ("sc.exe", "config", "WSearch", "start=", "delayed-auto"))

    def test_worker_does_not_mutate_when_uac_changes_profile(self):
        with TemporaryDirectory() as directory:
            home = Path(directory) / "admin"
            with patch.object(self.actions, "HOME", home), patch.object(self.actions, "execute") as execute:
                code = self.actions.worker("repair_disk", "acao-" + "a" * 32 + ".json", str(home.parent / "user"))
            execute.assert_not_called()
            self.assertEqual(code, 3)
            self.assertFalse(home.exists())

    def test_service_restore_attempts_other_services_and_retains_failed_backup(self):
        backup = {"svc": {"SysMain": 3, "WSearch": 2}}

        def configure(*args):
            if args[2] == "SysMain":
                raise RuntimeError("Acesso negado a SysMain")
            return "OK"

        with patch.object(self.actions, "winreg", create=True), \
                patch.object(self.actions, "load", return_value=backup), \
                patch.object(self.actions, "save"), patch.object(self.actions, "cmd", side_effect=configure):
            with self.assertRaisesRegex(RuntimeError, "Acesso negado a SysMain"):
                self.actions.services(("SysMain", "WSearch"), False)
        self.assertEqual(backup["svc"], {"SysMain": 3})
