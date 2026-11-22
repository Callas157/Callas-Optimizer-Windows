"""Dois cartões para ChatGPT e Codex, um só aplicativo oficial e sem acesso implícito a dados."""
import ast
import re
from pathlib import Path
from xml.etree import ElementTree
import unittest

ROOT = Path(__file__).resolve().parents[1]

class OpenAIProgramsTest(unittest.TestCase):
    def test_official_download_only(self):
        gui=(ROOT/'src/app.py').read_text(encoding='utf-8')
        ast.parse(gui)
        for item in ('self.chatgpt_card', 'self.codex_card',
                     'open_openai_download("ChatGPT")', 'open_openai_download("Codex")',
                     'https://chatgpt.com/download/', 'https://learn.chatgpt.com/pt-BR/docs/quickstart'):
            self.assertIn(item, gui)
        action=gui.split('    def open_openai_download(',1)[1].split('    def install_extra(',1)[0]
        self.assertNotIn('subprocess', action)
        self.assertNotIn('Start-Process', action)
        self.assertNotIn('RunAs', action)
        self.assertNotIn('openai.api_key', action)

    def test_two_cards_but_one_installer(self):
        gui=(ROOT/'src/app.py').read_text(encoding='utf-8')
        self.assertEqual(gui.count('webbrowser.open("https://chatgpt.com/download/")'), 1)
        self.assertIn('Não é necessário instalar dois aplicativos.', gui)

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
