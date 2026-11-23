"""Teste de limpeza real somente dentro de uma pasta temporaria do teste."""
from pathlib import Path
import ctypes
import tempfile
import threading
import unittest
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from cleaner import clean_folders, clear_icon_cache, empty_recycle_bin, format_size, nvidia_dxcache_folders


class CleanerTests(unittest.TestCase):
    def test_icon_cache_removes_only_icon_databases(self):
        with tempfile.TemporaryDirectory() as profile:
            local = Path(profile) / "Local"
            explorer = local / "Microsoft" / "Windows" / "Explorer"
            explorer.mkdir(parents=True)
            removed = [local / "IconCache.db", explorer / "iconcache_256.db"]
            kept = [explorer / "thumbcache_256.db", explorer / "iconcache-notes.txt"]
            for path in removed + kept:
                path.write_bytes(b"fixture")
            with patch.dict("cleaner.os.environ", {"LOCALAPPDATA": str(local)}):
                with patch("cleaner.refresh_shell_icons") as refresh:
                    self.assertEqual(clear_icon_cache(), (2, 0))
                    refresh.assert_called_once_with()
            self.assertTrue(all(not path.exists() for path in removed))
            self.assertTrue(all(path.exists() for path in kept))

    def test_nvidia_cleanup_only_accepts_dxcache_in_the_current_profile(self):
        with tempfile.TemporaryDirectory() as profile:
            local = Path(profile) / "Local"
            approved = [local / "NVIDIA" / "DXCache",
                        Path(profile) / "LocalLow" / "NVIDIA" / "DXCache",
                        Path(profile) / "LocalLow" / "NVIDIA" / "PerDriverVersion" / "DXCache"]
            unrelated = [local / "NVIDIA" / "GLCache", local / "Unrelated" / "DXCache"]
            for root in approved + unrelated:
                root.mkdir(parents=True)
                (root / "fixture").write_bytes(b"data")
            with patch.dict("cleaner.os.environ", {"LOCALAPPDATA": str(local)}):
                self.assertEqual(nvidia_dxcache_folders(), approved)
                result = clean_folders(approved + unrelated, threading.Event())
            self.assertEqual(result.files, len(approved))
            self.assertTrue(all(path.is_dir() for path in approved))
            self.assertTrue(all((path / "fixture").exists() for path in unrelated))

    @unittest.skipUnless(sys.platform == "win32", "Windows Shell API required")
    def test_empty_recycle_bin_is_reported_without_requesting_deletion(self):
        with patch.object(ctypes.windll.shell32, "SHQueryRecycleBinW", return_value=0):
            with patch.object(ctypes.windll.shell32, "SHEmptyRecycleBinW", return_value=-2147418113) as empty:
                self.assertEqual(empty_recycle_bin(), "já vazia")
        empty.assert_not_called()

    @unittest.skipUnless(sys.platform == "win32", "Windows Shell API required")
    def test_recycle_failure_with_remaining_items_keeps_real_hresult(self):
        with patch("cleaner.recycle_bin_items", return_value=1):
            with patch.object(ctypes.windll.shell32, "SHEmptyRecycleBinW", return_value=-2147418113):
                with self.assertRaisesRegex(OSError, r"0x8000FFFF"):
                    empty_recycle_bin()

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
