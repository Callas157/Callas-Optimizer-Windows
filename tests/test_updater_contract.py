"""Contratos estruturais de atualizacao; nao substituem teste Windows real."""
from pathlib import Path
import ast
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')
UPDATER = (ROOT / 'src/updater.ps1').read_text(encoding='utf-8')

class UpdateContract(unittest.TestCase):
    def test_python_gui_parses(self):
        ast.parse(APP)
        ast.parse((ROOT / 'src/cleaner.py').read_text(encoding='utf-8'))
    def test_supported_features(self):
        for name in ('QSplitter', 'QStackedWidget', 'QScrollArea', 'resizeEvent', 'QMainWindow',
                     '"Brave Browser", "brave"', '"NVIDIA App", "nvidia"', 'CleanerThread', 'QMessageBox.question'):
            self.assertIn(name, APP)
    def test_version_contract(self):
        ver = (ROOT / 'VERSION').read_text().strip()
        self.assertIn(f'APP_VERSION = "{ver}"', APP)
        self.assertEqual(len(re.findall(r'^APP_VERSION\s*=', APP, re.MULTILINE)), 1)
    def test_release_sha256(self):
        self.assertIn('Get-FileHash', UPDATER)
        self.assertIn('Confirm-WindowsExe $staged', UPDATER)
        self.assertIn('0x8664', UPDATER)
        self.assertIn("$Repository='Callas157/Callas-Optimizer-Windows'", UPDATER)
        self.assertNotIn('Callas157/arch-install', UPDATER)
    def test_update_prepares_before_exit(self):
        self.assertLess(UPDATER.index('Download-Verified $latest $staged'), UPDATER.index("Status 'READY'"))
        self.assertLess(UPDATER.index("Status 'READY'"), UPDATER.index('Wait-Process -Id $WaitPid'))
        self.assertIn('QApplication.quit()', APP)
    def test_maintains_13_menu_routes(self):
        for num in (1,2,3,4,5,6,8,9,10,12,13):
            self.assertRegex(APP, rf'\({num},\s*"')
        self.assertIn('("clean", "7  Limpeza Total"', APP)
        self.assertIn('("updates", "11  Atualizações"', APP)
    def test_source_assets_present(self):
        for p in ('assets/icons/brave.svg', 'assets/icons/nvidia.svg', 'assets/icons/callas.svg',
                  'src/Callas_Optimizer_V8_8_GUI_Engine.bat', 'src/updater.ps1',
                  'src/install_brave.ps1', 'src/install_nvidia.ps1'):
            self.assertTrue((ROOT / p).is_file(), p)

if __name__ == '__main__':
    unittest.main()
