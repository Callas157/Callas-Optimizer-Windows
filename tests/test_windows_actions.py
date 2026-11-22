"""Testes das funções Python Windows (não realizam mutações no runner)."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class NativeActionContracts(unittest.TestCase):
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
