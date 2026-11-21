"""Teste de limpeza real somente dentro de uma pasta temporaria do teste."""
from pathlib import Path
import tempfile
import threading
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cleaner import clean_folders, format_size


class CleanerTests(unittest.TestCase):
    def test_cleans_files_and_preserves_root(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / 'Temp'
            (root / 'nested').mkdir(parents=True)
            (root / 'foo.txt').write_bytes(b'abc')
            (root / 'nested' / 'bar.txt').write_bytes(b'12345')
            stats = clean_folders([root], threading.Event())
            self.assertEqual(stats.files, 2)
            self.assertEqual(stats.bytes_freed, 8)
            self.assertTrue(root.exists())
            self.assertEqual(list(root.iterdir()), [])
    def test_protects_arbitrary_directory(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / 'Documents'
            root.mkdir()
            target = root / 'keep.txt'
            target.write_text('do not delete')
            stats = clean_folders([root], threading.Event())
            self.assertEqual(stats.files, 0)
            self.assertTrue(target.exists())
    def test_honors_cancel(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / 'Temp'
            root.mkdir()
            (root / 'foo').write_text('keep')
            cancellation = threading.Event()
            cancellation.set()
            stats = clean_folders([root], cancellation)
            self.assertTrue(stats.cancelled)
            self.assertTrue((root / 'foo').exists())
    def test_size_format(self):
        self.assertEqual(format_size(1024), '1.0 KB')


if __name__ == '__main__':
    unittest.main()
