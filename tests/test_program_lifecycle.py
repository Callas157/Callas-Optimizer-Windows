from pathlib import Path
import subprocess
import ssl
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import extra_installers as installers


class ProgramLifecycleTest(unittest.TestCase):
    def test_downloader_uses_windows_trust_and_preserves_hostname_checks(self):
        import truststore
        with patch.object(installers.urllib.request, "build_opener") as build:
            build.return_value.open.side_effect = OSError("sentinel")
            with self.assertRaisesRegex(OSError, "sentinel"):
                installers._download_setup(installers.CATALOG["spotify"], Path("SpotifySetup.exe"),
                                           lambda *_: None)
        handlers = build.call_args.args
        https = next(handler for handler in handlers
                     if isinstance(handler, installers.urllib.request.HTTPSHandler))
        self.assertIsInstance(https._context, truststore.SSLContext)
        self.assertTrue(https._context.check_hostname)
        self.assertEqual(https._context.verify_mode, ssl.CERT_REQUIRED)

    def test_steam_retries_elevation_only_when_windows_requires_it(self):
        error = OSError("elevation required")
        error.winerror = 740
        path = Path("C:/Downloads/SteamSetup.exe")
        with patch.object(installers.subprocess, "Popen", side_effect=error):
            with patch.object(installers, "_run_elevated", return_value=0) as run:
                self.assertEqual(installers._run_setup(path), 0)
        run.assert_called_once_with(path)

    def test_waits_for_installer_exit(self):
        process = Mock()
        process.wait.return_value = 1602
        with patch.object(subprocess, "Popen", return_value=process):
            self.assertEqual(installers._run_setup(Path("C:/Downloads/DiscordSetup.exe")), 1602)
        process.wait.assert_called_once_with()

    def test_brave_reports_updater_lock_as_retryable(self):
        with self.assertRaisesRegex(RuntimeError, "Aguarde e tente de novo"):
            installers._check_setup_exit(-2147219687, "brave")

    def test_upgrade_detection_uses_exact_catalog_ids(self):
        output = (
            "Nome          ID                     Versão       Disponível    Origem\n"
            "Discord       Discord.Discord        1.0.1        1.0.2        winget\n"
            "Steam Clone   Valve.SteamFake        1.0.1        1.0.2        winget\n"
            "Brave         Brave.Brave            1.0.1        1.0.2        winget\n"
        )
        self.assertEqual(installers._upgrade_ids(output), {"discord", "brave"})

    def test_download_sources_have_explicit_security_boundaries(self):
        self.assertFalse(installers._safe_https("https://user@discord.com/test", {"discord.com"}))
        self.assertFalse(installers._safe_https("https://discord.com:444/test", {"discord.com"}))
        self.assertTrue(installers.CATALOG["brave"]["url"].endswith("/BraveBrowserStandaloneSetup.exe"))
        self.assertEqual(installers.CATALOG["epic"]["filename"], "EpicGamesLauncherInstaller.msi")

    def test_update_setup_has_visible_wizard(self):
        root = Path(__file__).resolve().parents[1]
        updater = (root / "src/updater.ps1").read_text(encoding="utf-8")
        setup_line = next(line for line in updater.splitlines() if "$setup=Start-Process" in line)
        self.assertIn("/CALLASUPDATE", setup_line)
        self.assertIn("/SILENT", setup_line)
        self.assertNotIn("/VERYSILENT", setup_line)
        installer = (root / "installer/CallasOptimizer.iss").read_text()
        self.assertIn("CurPageChanged", installer)
        self.assertIn("function PrepareToInstall", installer)
        self.assertIn("close_running_app.ps1", installer)
