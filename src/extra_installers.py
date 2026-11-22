"""Instala, identifica e abre programas do catálogo do Callas Optima."""
from __future__ import annotations

from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request

ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CallasTeck" / "Downloads"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
SUCCESS_CODES = {0, 1641, 3010}

CATALOG = {
    "brave": {
        "name": "Brave Browser",
        "url": "https://github.com/brave/brave-browser/releases/latest/download/BraveBrowserStandaloneSetup.exe",
        "website": "https://brave.com/download/",
        "hosts": {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"},
        "publisher": r"Brave Software(?:,? Inc\.?)?",
        "filename": "BraveBrowserStandaloneSetup.exe",
    },
    "nvidia": {
        "name": "NVIDIA App",
        "url": "https://us.download.nvidia.com/nvapp/client/11.0.9.585/x64/NVIDIA_app_v11.0.9.585_x64.exe",
        "website": "https://www.nvidia.com/pt-br/software/nvidia-app/",
        "hosts": {"us.download.nvidia.com"},
        "publisher": r"NVIDIA Corporation",
        "filename": "NVIDIA_App_Setup.exe",
    },
    "discord": {
        "name": "Discord",
        "url": "https://discord.com/api/downloads/distributions/app/installers/latest?arch=x64&channel=stable&platform=win",
        "website": "https://discord.com/download",
        "hosts": {"discord.com", "dl.discordapp.net", "dl2.discordapp.net", "stable.dl2.discordapp.net", "updates.discord.com"},
        "publisher": r"Discord(?:,? Inc\.?)?",
        "filename": "DiscordSetup.exe",
    },
    "steam": {
        "name": "Steam",
        "url": "https://cdn.akamai.steamstatic.com/client/installer/SteamSetup.exe",
        "website": "https://store.steampowered.com/about/",
        "hosts": {"cdn.akamai.steamstatic.com", "steamcdn-a.akamaihd.net", "media.steampowered.com"},
        "publisher": r"Valve(?: Corporation| Corp\.?)?",
        "filename": "SteamSetup.exe",
    },
    "medal": {
        "name": "Medal",
        "url": "https://install.medal.tv/",
        "website": "https://medal.tv/pt/download/pc",
        "hosts": {"install.medal.tv", "cdn.medal.tv"},
        "publisher": r"Medal(?: B\.?V\.?|(?:,? Inc\.?))?",
        "filename": "MedalSetup.exe",
    },
    "lghub": {
        "name": "Logitech G HUB",
        "url": "https://download01.logi.com/web/ftp/pub/techsupport/gaming/lghub_installer.exe",
        "website": "https://www.logitechg.com/pt-br/software/ghub",
        "hosts": {"download01.logi.com"},
        "publisher": r"Logitech(?: Europe)?(?: S\.?A\.?| Inc\.?)?",
        "filename": "LGHUB_Installer.exe",
    },
    "spotify": {
        "name": "Spotify",
        "url": "https://download.scdn.co/SpotifySetup.exe",
        "website": "https://www.spotify.com/br/download/windows/",
        "hosts": {"download.scdn.co"},
        "publisher": r"Spotify(?: AB)?",
        "filename": "SpotifySetup.exe",
    },
    "epic": {
        "name": "Epic Games Launcher",
        "url": "https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi",
        "website": "https://store.epicgames.com/download",
        "hosts": {"launcher-public-service-prod06.ol.epicgames.com", "epicgames-download1.akamaized.net",
                  "download.epicgames.com", "launcher-download.epicgames.com"},
        "publisher": r"Epic Games(?:,? Inc\.?)?",
        "filename": "EpicGamesLauncherInstaller.msi",
    },
    "wise": {
        "name": "Wise Program Uninstaller",
        "url": "https://www.wisecleaner.com/index.php?product=wise-program-uninstaller&r=download-product%2Flatest-version",
        "website": "https://www.wisecleaner.com/wise-program-uninstaller.html",
        "hosts": {"downloads.wisecleaner.com", "www.wisecleaner.com", "www.wisecleaner.eu"},
        "publisher": r"Lespeed Technology(?: Co\.?,?)? Ltd\.?",
        "filename": "WPUSetup.exe",
    },
}

WINGET_IDS = {
    "brave": "Brave.Brave", "discord": "Discord.Discord", "steam": "Valve.Steam",
    "epic": "EpicGames.EpicGamesLauncher", "wise": "WiseCleaner.WiseProgramUninstaller",
    "lghub": "Logitech.GHUB", "spotify": "Spotify.Spotify",
}

PROGRAM_PATHS = {
    "brave": r"BraveSoftware\Brave-Browser\Application\brave.exe",
    "nvidia": r"NVIDIA Corporation\NVIDIA App\CEF\NVIDIA App.exe",
    "discord": r"Discord\app-*\Discord.exe",
    "steam": r"Steam\steam.exe",
    "medal": r"Medal\app-*\Medal.exe",
    "lghub": r"LGHUB\lghub.exe",
    "spotify": r"Spotify\Spotify.exe",
    "epic": r"Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
    "wise": r"Wise\Wise Program Uninstaller\WiseProgramUninstaller.exe",
}


def official_website(app_id: str) -> str:
    return CATALOG[app_id]["website"]


def _safe_https(url: str, hosts: set[str]) -> bool:
    try:
        parsed = urllib.parse.urlsplit(url)
        return (parsed.scheme == "https" and parsed.hostname in hosts
                and parsed.port in (None, 443) and parsed.username is None)
    except ValueError:
        return False


class _OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed: set[str]):
        super().__init__()
        self.allowed = allowed

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not _safe_https(newurl, self.allowed):
            raise RuntimeError("O site redirecionou para um endereço que não é oficial.")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def powershell_path() -> Path:
    return _system_program(r"WindowsPowerShell\v1.0\powershell.exe")


def powershell_env() -> dict[str, str]:
    return {**os.environ, "PSModulePath": str(powershell_path().parent / "Modules")}


def _system_program(relative: str) -> Path:
    if os.name == "nt":
        buffer = ctypes.create_unicode_buffer(32768)
        length = ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
        if 0 < length < len(buffer):
            return Path(buffer.value) / relative
    raise OSError("A pasta de sistema do Windows está indisponível.")


def verify_authenticode(path: Path, publisher_regex: str) -> str:
    """Exige cadeia Authenticode confiável e editor esperado."""
    import base64
    ps_path = str(path).replace("'", "''")
    command = (
        "$ErrorActionPreference='Stop'; "
        f"$s=Get-AuthenticodeSignature -LiteralPath '{ps_path}'; "
        "if($s.Status -ne 'Valid' -or $null -eq $s.SignerCertificate){ exit 12 }; "
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
        "[Console]::WriteLine($s.SignerCertificate.GetNameInfo('SimpleName',$false))"
    )
    encoded = base64.b64encode(command.encode("utf-16le")).decode("ascii")
    result = subprocess.run(
        [str(powershell_path()), "-NoLogo", "-NoProfile", "-NonInteractive",
         "-EncodedCommand", encoded],
        text=True, capture_output=True, encoding="utf-8", errors="replace",
        timeout=45, shell=False,
        creationflags=NO_WINDOW,
        env=powershell_env(),
    )
    signer = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(publisher_regex, signer, re.I):
        raise RuntimeError("Assinatura digital inválida ou editor não reconhecido. "
                           "Instalação bloqueada por segurança.")
    return signer


def installed_program(app_id: str) -> Path | None:
    if os.name != "nt":
        return None
    if app_id == "steam":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                candidate = Path(winreg.QueryValueEx(key, "SteamExe")[0])
                if (candidate.is_absolute() and not candidate.drive.startswith("\\\\")
                        and candidate.name.lower() == "steam.exe" and candidate.is_file()):
                    return candidate
        except (OSError, TypeError):
            pass
    pattern = PROGRAM_PATHS[app_id]
    for variable in ("LOCALAPPDATA", "APPDATA", "ProgramFiles", "ProgramFiles(x86)"):
        directory = os.environ.get(variable)
        if not directory:
            continue
        found = [path for path in Path(directory).glob(pattern) if path.is_file()]
        if found:
            if "app-*" in pattern:
                def version(path):
                    return tuple(int(part) for part in re.findall(r"\d+", path.parent.name))
                return max(found, key=version)
            return found[0]
    return None


def winget_path() -> Path:
    return ROOT.parent.parent / "Microsoft" / "WindowsApps" / "winget.exe"


def _upgrade_ids(output: str) -> set[str]:
    ids = {package.casefold(): app for app, package in WINGET_IDS.items()}
    available = set()
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[-1].casefold() == "winget":
            fields.pop()
        # Depois do nome, a tabela traz ID, versão instalada e versão disponível.
        if len(fields) >= 4 and fields[-3].casefold() in ids:
            available.add(ids[fields[-3].casefold()])
    return available


def available_upgrades() -> set[str] | None:
    if os.name != "nt":
        return None
    try:
        result = subprocess.run(
            [str(winget_path()), "list", "--upgrade-available", "--source", "winget",
             "--disable-interactivity"], capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=35, creationflags=NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode & 0xFFFFFFFF in (0x8A150014, 0x8A15002B):
        return set()
    return _upgrade_ids(result.stdout) if result.returncode == 0 else None


def upgrade_program(app_id: str, notify) -> None:
    notify("Atualizando pelo WinGet…", -1)
    result = subprocess.run(
        [str(winget_path()), "upgrade", "--id", WINGET_IDS[app_id], "--exact",
         "--source", "winget", "--interactive", "--disable-interactivity"],
        stdin=subprocess.DEVNULL, creationflags=NO_WINDOW,
    )
    if result.returncode & 0xFFFFFFFF == 0x8A15002B:
        # O programa pode ter recebido a atualização sozinho entre a consulta e o clique.
        return
    _check_setup_exit(result.returncode)


class _ShellExecuteInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("fMask", ctypes.c_ulong),
        ("hwnd", wintypes.HWND), ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR), ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR), ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE), ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR), ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD), ("hIcon", wintypes.HANDLE), ("hProcess", wintypes.HANDLE),
    ]


def _run_elevated(executable: Path) -> int:
    """Abre o diálogo UAC padrão e aguarda o processo retornado pelo Shell."""
    info = _ShellExecuteInfo()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = 0x00000040 | 0x00000100  # NOCLOSEPROCESS | NOASYNC
    info.lpVerb = "runas"
    info.lpFile = str(executable)
    info.lpDirectory = str(executable.parent)
    info.nShow = 1
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    ole = ctypes.WinDLL("ole32")
    shell.ShellExecuteExW.argtypes = [ctypes.POINTER(_ShellExecuteInfo)]
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    initialized = ole.CoInitializeEx(None, 0x2) in (0, 1)
    try:
        if not shell.ShellExecuteExW(ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not info.hProcess:
            raise RuntimeError("O Windows não retornou um processo de instalação.")
        try:
            if kernel.WaitForSingleObject(info.hProcess, 0xFFFFFFFF) != 0:
                raise ctypes.WinError(ctypes.get_last_error())
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(info.hProcess, ctypes.byref(code)):
                raise ctypes.WinError(ctypes.get_last_error())
            return code.value
        finally:
            kernel.CloseHandle(info.hProcess)
    finally:
        if initialized:
            ole.CoUninitialize()


def _run_setup(executable: Path) -> int:
    command = [str(executable)]
    if executable.suffix == ".msi":
        command = [str(_system_program("msiexec.exe")), "/i", str(executable), "/norestart"]
    try:
        process = subprocess.Popen(command, cwd=executable.parent, creationflags=NO_WINDOW, shell=False)
    except OSError as exc:
        if getattr(exc, "winerror", None) != 740 or executable.suffix != ".exe":
            raise
        return _run_elevated(executable)
    return process.wait()


def _check_setup_exit(code: int, app_id: str | None = None) -> None:
    if code in SUCCESS_CODES:
        return
    if code in (1602, 1223):
        raise RuntimeError("A instalação foi cancelada.")
    if app_id == "brave" and code & 0xFFFFFFFF == 0x80040719:
        raise RuntimeError("O Brave já está instalando ou atualizando em segundo plano. "
                           "Aguarde e tente de novo (0x80040719).")
    raise RuntimeError(f"O instalador retornou o código {code} (0x{code & 0xFFFFFFFF:08X}).")


@contextmanager
def _read_only_installer(path: Path):
    """Bloqueia gravação e troca do arquivo verificável durante a instalação."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                   ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateFileW(str(path), 0x80000000, 1, None, 3, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        yield
    finally:
        kernel.CloseHandle(handle)


def download_and_open(app_id: str, notify) -> None:
    """Executa apenas o instalador oficial verificado e espera a conclusão."""
    if os.name != "nt":
        raise OSError("Os instaladores são exclusivos para Windows.")
    if app_id not in CATALOG:
        raise ValueError("Aplicativo não cadastrado.")
    if app_id == "nvidia":
        _check_nvidia_gpu()
    app = CATALOG[app_id]
    if not _safe_https(app["url"], app["hosts"]):
        raise ValueError("URL de download não autorizada.")
    ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{app_id}-", dir=ROOT, ignore_cleanup_errors=True) as folder:
        executable = Path(folder) / app["filename"]
        _download_setup(app, executable, notify)
        # Preserva a marca de arquivo obtido da Internet em volumes NTFS.
        with open(f"{executable}:Zone.Identifier", "w", encoding="ascii") as zone:
            zone.write("[ZoneTransfer]\nZoneId=3\n")
        with _read_only_installer(executable):
            notify("Verificando assinatura digital…", -1)
            verify_authenticode(executable, app["publisher"])
            notify("Instalando…", -1)
            _check_setup_exit(_run_setup(executable), app_id)


def _check_nvidia_gpu() -> None:
    query = (
        "$ErrorActionPreference='Stop'; "
        "if (!(Get-CimInstance Win32_VideoController | Where-Object Name -match 'NVIDIA')) { exit 1 }"
    )
    result = subprocess.run(
        [str(powershell_path()), "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", query],
        stdin=subprocess.DEVNULL, capture_output=True, timeout=30, creationflags=NO_WINDOW,
        env=powershell_env(),
    )
    if result.returncode:
        raise RuntimeError("O Windows não identificou uma GPU NVIDIA compatível.")


def _download_setup(app, executable: Path, notify) -> None:
    notify("Baixando…", -1)
    opener = urllib.request.build_opener(_OfficialRedirects(app["hosts"]))
    request = urllib.request.Request(app["url"], headers={"User-Agent": "CallasOptima"})
    maximum = 512 * 1024 * 1024
    magic = bytes.fromhex("D0CF11E0A1B11AE1") if executable.suffix == ".msi" else b"MZ"
    size = 0
    last_progress = -1
    with opener.open(request, timeout=45) as response:
        if not _safe_https(response.geturl(), app["hosts"]):
            raise RuntimeError("URL final do download não é do fornecedor oficial.")
        total = int(response.headers.get("Content-Length") or 0)
        if not 0 <= total <= maximum:
            raise RuntimeError("Tamanho de download fora do limite permitido.")
        with executable.open("xb") as output:
            while block := response.read(256 * 1024):
                if size == 0 and not block.startswith(magic):
                    raise RuntimeError("O servidor não entregou um instalador Windows.")
                size += len(block)
                if size > maximum or (total and size > total):
                    raise RuntimeError("Download excedeu o tamanho permitido.")
                output.write(block)
                if total:
                    progress = size * 100 // total
                    if progress != last_progress:
                        notify("Baixando…", progress)
                        last_progress = progress
    if size < 100 * 1024 or (total and size != total):
        raise RuntimeError("O download do instalador está incompleto.")
