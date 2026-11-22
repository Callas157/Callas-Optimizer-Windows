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
                     '"Brave Browser", "brave"', '"NVIDIA App", "nvidia"', 'CleanerThread', 'confirmar(self,'):
            self.assertIn(name, APP)
    def test_version_contract(self):
        ver = (ROOT / 'VERSION').read_text().strip()
        self.assertIn(f'APP_VERSION = "{ver}"', APP)
        self.assertEqual(len(re.findall(r'^APP_VERSION\s*=', APP, re.MULTILINE)), 1)
    def test_programs_right_after_home(self):
        section = APP.split("NAV_SECTIONS = [", 1)[1].split("LEGACY = {", 1)[0]
        self.assertLess(section.index('("home", "Início"'), section.index('("programs", "Programas"'))
        self.assertLess(section.index('("programs", "Programas"'), section.index('("gamer", "Modo Gamer"'))
        self.assertNotIn('("APLICATIVOS",', section)

    def test_update_stage_filename_readable(self):
        self.assertIn("Join-Path $sessionDir 'Callas Optimizer.exe'", UPDATER)
        self.assertIn('Join-Path $stageDir $latest.Tag', UPDATER)
        self.assertIn('Start-Process -FilePath $staged', UPDATER)
        self.assertNotIn("Join-Path $stageDir ([guid]::NewGuid().ToString('N')+'.exe')", UPDATER)

    def test_setup_identity_before_uac(self):
        self.assertIn('function Confirm-StagedSetupIdentity', UPDATER)
        self.assertIn("Join-Path $sessionDir 'Callas Optimizer.exe'", UPDATER)
        self.assertLess(UPDATER.index("Confirm-StagedSetupIdentity $staged"),
                        UPDATER.index("Status 'READY'"))
        self.assertLess(UPDATER.index("Confirm-StagedSetupIdentity $staged"),
                        UPDATER.index("Start-Process -FilePath $staged"))
        self.assertIn('FileDescription.Trim()', UPDATER)
        self.assertIn('ProductName.Trim()', UPDATER)
        self.assertIn('Abrindo UAC do instalador:', UPDATER)

    def test_direct_cumulative_upgrade(self):
        # A ultima versao contem todas as mudancas; nao executamos upgrades
        # intermediarios nem dependemos de assets portateis antigos.
        self.assertIn("'/releases/latest'", UPDATER)
        self.assertIn("if ($latest.Version -le [version]$CurrentVersion)", UPDATER)
        self.assertIn("Callas_Optimizer_Setup_x64.exe", UPDATER)
        self.assertIn("Start-Process -FilePath $staged", UPDATER)
        installer=(ROOT / 'installer/CallasOptimizer.iss').read_text(encoding='utf-8')
        self.assertIn("AppId={{33D8076A-342F-4AF7-8D18-1885BF08FC04}", installer)
        self.assertIn('DefaultDirName={autopf}\\Callas Optimizer', installer)
        self.assertIn('#define MyAppExe "Callas_Optimizer_Windows_x64.exe"', installer)
        smoke=(ROOT / 'scripts/test_direct_upgrade.ps1').read_text(encoding='utf-8')
        for term in ('v8.9.3','Get-FileHash','Install-Silent $oldSetup',
                     "Install-Silent $CurrentSetup", "'--self-test'"):
            self.assertIn(term, smoke)
        workflow=(ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8')
        self.assertIn("scripts/test_direct_upgrade.ps1", workflow)

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
        nav = APP.split("NAV_SECTIONS = [", 1)[1].split("LEGACY = {", 1)[0]
        for route, title in (
            ("gamer", "Modo Gamer"), ("edge", "Microsoft Edge"),
            ("windows_update", "Windows Update"), ("network", "Rede e DNS"),
            ("privacy", "Privacidade"), ("repair", "Reparar Windows"),
            ("clean", "Limpeza Total"), ("classic", "Menu clássico"),
            ("shutdown", "Desligamento"), ("winutil", "WinUtil"),
            ("updates", "Atualizações"), ("restore_point", "Ponto de restauração"),
            ("restore", "Restaurar padrões"),
        ):
            self.assertIn(f'("{route}", "{title}"', nav)
        self.assertNotRegex(nav, r'\("[^"]+",\s*"[0-9]+\s')
    def test_source_assets_present(self):
        for p in ('assets/icons/brave.svg', 'assets/icons/nvidia.svg', 'assets/icons/callas.svg',
                  'src/windows_actions.py', 'src/updater.ps1',
                  'src/extra_installers.py', 'src/extensions.ps1', 'src/undo_extensions.ps1'):
            self.assertTrue((ROOT / p).is_file(), p)

if __name__ == '__main__':
    unittest.main()
