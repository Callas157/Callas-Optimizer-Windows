"""Contratos dos três instaladores adicionais, sem download externo em CI."""
import ast
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from extra_installers import _safe_https, CATALOG

ROOT = Path(__file__).resolve().parents[1]


class ExtraInstallersTest(unittest.TestCase):
    def test_module_and_whitelist(self):
        code = (ROOT / 'src/extra_installers.py').read_text(encoding='utf-8')
        ast.parse(code)
        for expected in ('install.medal.tv', 'cdn.medal.tv', 'download01.logi.com',
                         'download.scdn.co', 'Get-AuthenticodeSignature',
                         'SpotifySetup.exe', 'MedalSetup.exe', 'LGHUB_Installer.exe'):
            self.assertIn(expected, code)
        self.assertIn('shell=False', code)
        self.assertIn('_OfficialRedirects', code)

    def test_gui_has_five_cards(self):
        code = (ROOT / 'src/app.py').read_text(encoding='utf-8')
        ast.parse(code)
        for needle in ('self.medal_card', 'self.lghub_card', 'self.spotify_card',
                       'self.install_extra("medal")', 'self.install_extra("lghub")',
                       'self.install_extra("spotify")', 'all_program_cards'):
            self.assertIn(needle, code)

    def test_version(self):
        version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
        self.assertIn('APP_VERSION = "' + version + '"',
                      (ROOT/'src/app.py').read_text(encoding='utf-8'))

    def test_official_https_only(self):
        for app in CATALOG.values():
            self.assertTrue(_safe_https(app["url"], app["hosts"]))
            self.assertFalse(_safe_https(app["url"].replace("https://", "http://"), app["hosts"]))
            self.assertFalse(_safe_https("https://phishing.invalid/" + app["url"], app["hosts"]))
            self.assertTrue(app["publisher"])

    def test_staging_is_isolated_and_verifies_before_execution(self):
        installer = (ROOT / "src/extra_installers.py").read_text(encoding="utf-8")
        self.assertIn("tempfile.TemporaryDirectory", installer)
        self.assertLess(installer.index('verify_authenticode(executable, app["publisher"])'),
                        installer.index("_check_setup_exit(_run_setup(executable), app_id)"))
        app = (ROOT / "src/app.py").read_text(encoding="utf-8")
        self.assertNotIn("self.extra_installer.finished.connect(self.extra_installer.deleteLater)", app)

    def test_virtualbox_catalogue_and_integrity(self):
        from extra_installers import parse_virtualbox_release, WINGET_IDS, PROGRAM_PATHS
        v = CATALOG["virtualbox"]
        self.assertEqual(v["hosts"], {"download.virtualbox.org"})
        self.assertEqual(v["filename"], "VirtualBox-Windows-Setup.exe")
        self.assertEqual(WINGET_IDS["virtualbox"], "Oracle.VirtualBox")
        self.assertIn(r"Oracle\VirtualBox\VirtualBox.exe", PROGRAM_PATHS["virtualbox"])
        sample = 'VirtualBox-7.2.22-175245-Win.exe'
        url, digest = parse_virtualbox_release(
            "7.2.22", f'<a href="{sample}">{sample}</a>',
            'a'*64 + ' *' + sample + '\n')
        self.assertEqual(url, "https://download.virtualbox.org/virtualbox/7.2.22/" + sample)
        self.assertEqual(digest, "a"*64)
        with self.assertRaises(RuntimeError):
            parse_virtualbox_release("../7.2.22", sample, 'a'*64 + ' *' + sample)
        with self.assertRaises(RuntimeError):
            parse_virtualbox_release("7.2.22", sample, 'b'*64 + ' *other.exe')
        src = (ROOT/"src/extra_installers.py").read_text(encoding="utf-8")
        self.assertLess(src.index("actual_sha256.lower() != expected_sha256"),
                        src.index('verify_authenticode(executable, app["publisher"])'))
        self.assertLess(src.index('verify_authenticode(executable, app["publisher"])'),
                        src.index('_check_setup_exit(_run_setup(executable), app_id)'))

    def test_virtualbox_gui_card(self):
        gui = (ROOT/"src/app.py").read_text(encoding="utf-8")
        self.assertIn('self.virtualbox_card = self._program_card(', gui)
        self.assertIn('self.install_extra("virtualbox")', gui)
        self.assertIn('self.virtualbox_card, self.medal_card', gui)
