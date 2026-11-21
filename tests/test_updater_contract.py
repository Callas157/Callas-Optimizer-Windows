"""Testes estaticos; Windows 11 deve ser testado em maquina real."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class Contract(unittest.TestCase):
    def test_gui_stays_open_during_download(self):
        s=(R/'src/app.c').read_text()
        a=s[s.index('static void install_update(void){'):s.index('static void poll_update_install(void){')]
        self.assertNotIn('ExitProcess(0)',a)
        self.assertIn('SetTimer(mainwin,84',a)
        self.assertIn('-StatusFile',a)
    def test_ready_only_after_download_validation_and_stage(self):
        s=(R/'src/updater.ps1').read_text()
        a=s.index('Download-Verified $latest $staged')
        b=s.index('Copy-Item -LiteralPath $staged -Destination $neighbor',a)
        c=s.index("Status 'READY'",b)
        d=s.index('Wait-Process -Id $WaitPid',c)
        self.assertLess(a,b)
        self.assertLess(b,c)
        self.assertLess(c,d)
    def test_sha256_and_pe_checks(self):
        s=(R/'src/updater.ps1').read_text()
        self.assertIn('Get-FileHash',s)
        self.assertIn('Confirm-WindowsExe $staged',s)
        self.assertIn('0x8664',s)
    def test_repository_only(self):
        s=(R/'src/updater.ps1').read_text()
        self.assertIn("$Repository='Callas157/Callas-Optimizer-Windows'",s)
        self.assertNotIn('Callas157/arch-install',s)
if __name__=='__main__':unittest.main()
