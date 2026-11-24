from pathlib import Path
import subprocess
import ssl
import tempfile
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import extra_installers as installers


class ProgramLifecycleTest(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows paths required")
    def test_medal_recognizes_current_launcher_and_legacy_layouts(self):
        for relative in (r"Medal\Medal.exe", r"Medal\current\Medal.exe",
                         r"Programs\Medal\Medal.exe", r"Medal\app-2.1.0\Medal.exe"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as directory:
                with patch.dict(installers.os.environ, {"LOCALAPPDATA": directory}, clear=True):
                    executable = Path(directory) / relative
                    executable.parent.mkdir(parents=True)
                    executable.touch()
                    self.assertEqual(installers.installed_program("medal"), executable)

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

    def test_spotify_update_attempts_exact_winget_package_without_a_scan(self):
        with patch.object(installers, "installed_program", return_value=Path("Spotify.exe")), \
                patch.object(installers.subprocess, "run", return_value=Mock(returncode=0x8A15002B)) as run:
            message = installers.upgrade_program("spotify", lambda *_: None)
        command = run.call_args.args[0]
        self.assertEqual(command[1:5], ["upgrade", "--id", "Spotify.Spotify", "--exact"])
        self.assertIn("atualização aplicável", message)

    def test_package_missing_uses_verified_manufacturer_installer(self):
        with patch.object(installers, "installed_program", return_value=Path("Spotify.exe")), \
                patch.object(installers.subprocess, "run", return_value=Mock(returncode=0x8A150014)), \
                patch.object(installers, "download_and_open") as official:
            installers.upgrade_program("spotify", lambda *_: None)
        self.assertEqual(official.call_args.args[0], "spotify")

    def test_unavailable_winget_source_uses_manufacturer_installer(self):
        with patch.object(installers, "installed_program", return_value=Path("Spotify.exe")), \
                patch.object(installers.subprocess, "run", return_value=Mock(returncode=0x8A15004B)), \
                patch.object(installers, "download_and_open") as official:
            installers.upgrade_program("spotify", lambda *_: None)
        self.assertEqual(official.call_args.args[0], "spotify")

    def test_codex_update_opens_the_shared_store_listing(self):
        with patch.object(installers, "open_program") as open_program:
            message = installers.upgrade_program("codex", lambda *_: None)
        open_program.assert_called_once_with("ms-windows-store://pdp/?ProductId=9PLM9XGG6VKS")
        self.assertIn("Microsoft Store", message)

    def test_spotify_store_package_is_detected_without_a_desktop_copy(self):
        def enumerate_packages(family, count, *_):
            self.assertEqual(family, "SpotifyAB.SpotifyMusic_zpdnekdrzrea0")
            uint_pointer = installers.ctypes.POINTER(installers.wintypes.UINT)
            installers.ctypes.cast(count, uint_pointer).contents.value = 1
            return 122

        with patch.object(installers, "os", SimpleNamespace(name="nt", environ={})), \
                patch.object(installers.ctypes, "windll", create=True) as windows:
            windows.kernel32.GetPackagesByPackageFamily.side_effect = enumerate_packages
            self.assertEqual(installers.installed_program("spotify"),
                             r"shell:AppsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify")

    def test_spotify_from_the_store_updates_through_its_own_listing(self):
        target = r"shell:AppsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify"
        with patch.object(installers, "installed_program", return_value=target), \
                patch.object(installers, "open_program") as open_program:
            message = installers.upgrade_program("spotify", lambda *_: None)
        open_program.assert_called_once_with("ms-windows-store://pdp/?ProductId=9NCBCSZSJRSB")
        self.assertIn("Microsoft Store", message)

    def test_nvidia_update_resolves_the_current_x64_installer_from_the_vendor(self):
        base = "https://us.download.nvidia.com/nvapp/client/"
        official = base + "11.1.0.123/x64/NVIDIA_app_v11.1.0.123_x64.exe"
        with patch.object(installers, "official_https_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.geturl.return_value = "https://www.nvidia.com/pt-br/software/nvidia-app/"
            response.read.return_value = (
                f'<a href="{base}11.1.0.125/arm64/NVIDIA_app_v11.1.0.125_arm64.exe">'
                f'<a href="{official}">'
            ).encode()
            self.assertEqual(installers.resolve_nvidia_release(), official)

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
