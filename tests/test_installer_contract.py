"""Testes do instalador, versao, iconografia e atualizador."""
from pathlib import Path
import ast, base64, struct, unittest
R=Path(__file__).resolve().parents[1]
A=(R/'src/app.py').read_text(encoding='utf-8')
U=(R/'src/updater.ps1').read_text(encoding='utf-8')
I=(R/'installer/CallasOptimizer.iss').read_text(encoding='utf-8')
W=(R/'.github/workflows/release.yml').read_text(encoding='utf-8')
class InstallerTests(unittest.TestCase):
    def test_python_gui_icon(self):
        ast.parse(A)
        for t in ('def app_icon()', 'app.setWindowIcon(app_icon())', 'SetCurrentProcessExplicitAppUserModelID', 'installed.marker'):
            self.assertIn(t,A)
    def test_ico(self):
        b=base64.b64decode((R/'assets/icons/callas.ico.b64').read_text())
        self.assertEqual(b[:4],b'\0\0\x01\0')
        self.assertGreaterEqual(struct.unpack_from('<H',b,4)[0],5)
    def test_setup(self):
        for t in ('DefaultDirName={autopf}\\Callas Optimizer','UninstallDisplayIcon=','[Icons]','[Registry]','GetEnv("CALLAS_VERSION")'):
            self.assertIn(t,I)
    def test_shortcut_icon_paths(self):
        for value in (
            'Source: "..\\assets\\icons\\callas.ico"',
            'DestName: "CallasOptimizer.ico"',
            'UninstallDisplayIcon={app}\\CallasOptimizer.ico',
            'IconFilename: "{app}\\CallasOptimizer.ico"',
            'AppUserModelID: "CallasTeck.CallasOptimizer.Windows"',
        ):
            self.assertIn(value, I)
        self.assertEqual(I.count('IconFilename: "{app}\\CallasOptimizer.ico"'), 2)
        self.assertIn('CallasOptimizer.ico', A)
    def test_updater(self):
        for t in ("'Callas_Optimizer_Setup_x64.exe'",'if ($Installed)','-Verb RunAs','Get-FileHash'):
            self.assertIn(t,U)
    def test_workflow(self):
        self.assertIn('Testar instalacao e icones dos atalhos no Windows', W)
        self.assertIn('IconLocation', W)
        self.assertIn('O aplicativo INSTALADO nao abriu', W)
        self.assertIn('--self-test', W)
        for t in ('windows-latest','Inno Setup 6','Callas_Optimizer_Setup_x64.exe'):
            self.assertIn(t,W)
