"""Contratos dos três instaladores adicionais, sem download externo em CI."""
import ast
from pathlib import Path
import unittest

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
