"""Testes das funções Python Windows (não realizam mutações no runner)."""
import ast
from pathlib import Path
import sys
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
        ast.parse(s)
        for route in ('gamer','edge','windows_update','network','privacy','repair',
                      'classic','shutdown','winutil','restore_point','restore'):
            self.assertIn(f'"{route}"',s)
        self.assertIn('shell=False',s)
        self.assertIn('worker(action_id,filename)',s)
    def test_gui_no_bat(self):
        s=(ROOT/'src/app.py').read_text(encoding='utf-8')
        ast.parse(s)
        self.assertNotIn('start_admin_bat(',s)
        self.assertNotIn('GUI_Engine.bat',s)
        self.assertIn('self.native_action(code)',s)
        self.assertIn('--callas-task',s)
