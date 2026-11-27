"""Regressão da ativação inicial, sem depender de um desktop interativo."""
import ast
import ctypes
from ctypes import wintypes
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call


class StartupFocusTests(unittest.TestCase):
    def setUp(self):
        source = (Path(__file__).resolve().parents[1] / 'src/app.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'bring_startup_to_front')
        self.native = Mock()
        self.native.GetForegroundWindow.return_value = 10
        self.native.SetForegroundWindow.return_value = False
        self.native.SetWindowPos.return_value = True
        self.platform = Mock(return_value='windows')
        env = dict(ctypes=SimpleNamespace(WinDLL=Mock(return_value=self.native), c_int=ctypes.c_int),
                   wintypes=wintypes, os=SimpleNamespace(name='nt'),
                   QApplication=SimpleNamespace(platformName=self.platform))
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<startup>', 'exec'), env)
        self.activate = env['bring_startup_to_front']
        self.window = Mock()
        self.window.isVisible.return_value = True
        self.window.isMinimized.return_value = False
        self.window.winId.return_value = 20
        self.assertIn('QTimer.singleShot(0, lambda: bring_startup_to_front(window))', source)

    def test_denied_focus_raises_temporarily(self):
        self.activate(self.window)
        self.window.raise_.assert_called_once()
        self.window.activateWindow.assert_called_once()
        self.assertEqual(self.native.SetWindowPos.call_args_list, [
            call(20, -1, 0, 0, 0, 0, 19), call(20, -2, 0, 0, 0, 0, 19)])
        self.assertEqual(self.native.SetForegroundWindow.call_count, 2)

    def test_normal_focus_no_topmost_and_restore_if_minimized(self):
        self.window.isMinimized.return_value = True
        self.native.SetForegroundWindow.return_value = True
        self.activate(self.window)
        self.window.showNormal.assert_called_once()
        self.native.SetWindowPos.assert_not_called()

    def test_offscreen_and_hidden(self):
        self.platform.return_value = 'offscreen'
        self.activate(self.window)
        self.native.SetForegroundWindow.assert_not_called()
        self.window.reset_mock()
        self.window.isVisible.return_value = False
        self.activate(self.window)
        self.window.activateWindow.assert_not_called()
