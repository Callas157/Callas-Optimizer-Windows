"""Impede que a publicacao volte a oferecer EXE portatil."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseOnlySetup(unittest.TestCase):
    def test_release_uses_only_setup(self):
        w = (ROOT/'.github/workflows/release.yml').read_text(encoding='utf-8')
        publishing = w.split('- name: Publicar somente Setup na Release', 1)[1].split(
            '\n  remover-portateis-antigos:', 1)[0]
        self.assertIn('dist/Callas_Optimizer_Setup_x64.exe', publishing)
        self.assertIn('dist/SHA256SUMS.txt', publishing)
        self.assertNotIn('dist/Callas_Optimizer_Windows_x64.exe', publishing)
        self.assertIn('gh release upload', publishing)

    def test_cleanup_of_old_assets(self):
        w = (ROOT/'.github/workflows/release.yml').read_text(encoding='utf-8')
        self.assertIn('remover-portateis-antigos:', w)
        self.assertIn('gh api -X DELETE', w)

    def test_hash_only_setup(self):
        s = (ROOT/'scripts/verify_build.py').read_text(encoding='utf-8')
        self.assertIn("sha256(setup.read_bytes())", s)
        self.assertIn("setup.name", s)
        b = (ROOT/'scripts/build.py').read_text(encoding='utf-8')
        self.assertNotIn("dist/SHA256SUMS.txt", b)
