"""Dois cartões para ChatGPT e Codex, um só aplicativo oficial e sem acesso implícito a dados."""
import ast
from pathlib import Path
import sys
from xml.etree import ElementTree
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from extra_installers import CATALOG, _safe_https, program_key

class OpenAIProgramsTest(unittest.TestCase):
    def test_both_cards_use_the_in_app_downloader(self):
        gui=(ROOT/'src/app.py').read_text(encoding='utf-8')
        ast.parse(gui)
        for item in ('self.chatgpt_card', 'self.codex_card',
                     'self.install_extra("chatgpt")', 'self.install_extra("codex")',
                     'https://learn.chatgpt.com/pt-BR/docs/quickstart'):
            self.assertIn(item, gui)

    def test_two_cards_but_one_installer(self):
        self.assertEqual(program_key("codex"), program_key("chatgpt"))
        self.assertNotIn("codex", CATALOG)
        package = CATALOG["chatgpt"]
        self.assertTrue(_safe_https(package["url"], {"get.microsoft.com"}))
        self.assertIn("/installer/download/9PLM9XGG6VKS", package["url"])
        self.assertEqual(package["publisher"], "Microsoft Corporation")

    def test_vector_icons(self):
        for name in ('chatgpt', 'codex'):
            p=ROOT/'assets/icons'/f'{name}.svg'
            root=ElementTree.parse(p).getroot()
            self.assertTrue(root.tag.endswith('svg'))
            self.assertIn('viewBox',root.attrib)

    def test_version(self):
        v=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
        app=(ROOT/'src/app.py').read_text(encoding='utf-8')
        self.assertIn(f'APP_VERSION = "{v}"',app)

if __name__=='__main__':
    unittest.main()
