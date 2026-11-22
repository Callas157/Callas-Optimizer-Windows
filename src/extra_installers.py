"""Baixa instaladores oficiais do Medal, Logitech G HUB e Spotify.

Não requer WinGet, não contorna o SmartScreen, recusa executáveis sem
assinatura Authenticode válida e não executa o que não for de editor esperado.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request

ROOT = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CallasTeck" / "Downloads"

CATALOG = {
    "medal": {
        "name": "Medal",
        "url": "https://install.medal.tv/",
        "website": "https://medal.tv/pt/download/pc",
        "hosts": {"install.medal.tv", "cdn.medal.tv"},
        "publisher": r"Medal",
        "filename": "MedalSetup.exe",
    },
    "lghub": {
        "name": "Logitech G HUB",
        "url": "https://download01.logi.com/web/ftp/pub/techsupport/gaming/lghub_installer.exe",
        "website": "https://www.logitechg.com/pt-br/software/ghub",
        "hosts": {"download01.logi.com"},
        "publisher": r"Logitech",
        "filename": "LGHUB_Installer.exe",
    },
    "spotify": {
        "name": "Spotify",
        "url": "https://download.scdn.co/SpotifySetup.exe",
        "website": "https://www.spotify.com/br/download/windows/",
        "hosts": {"download.scdn.co"},
        "publisher": r"Spotify",
        "filename": "SpotifySetup.exe",
    },
}


def official_website(app_id: str) -> str:
    return CATALOG[app_id]["website"]


def _safe_https(url: str, hosts: set[str]) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme.lower() == "https" and (parsed.hostname or "").lower() in hosts


class _OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed: set[str]):
        super().__init__()
        self.allowed = allowed

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not _safe_https(newurl, self.allowed):
            raise RuntimeError("O site redirecionou para um endereço que não é oficial.")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def verify_authenticode(path: Path, publisher_regex: str) -> str:
    """Exige cadeia Authenticode confiável e editor esperado."""
    import base64
    ps_path = str(path).replace("'", "''")
    command = (
        "$ErrorActionPreference='Stop'; "
        f"$s=Get-AuthenticodeSignature -LiteralPath '{ps_path}'; "
        "if($s.Status -ne 'Valid' -or $null -eq $s.SignerCertificate){ exit 12 }; "
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
        "[Console]::WriteLine($s.SignerCertificate.Subject)"
    )
    encoded = base64.b64encode(command.encode("utf-16le")).decode("ascii")
    result = subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive",
         "-EncodedCommand", encoded],
        text=True, capture_output=True, encoding="utf-8", errors="replace",
        timeout=45, shell=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    signer = result.stdout.strip()
    if result.returncode != 0 or not re.search(publisher_regex, signer, re.I):
        raise RuntimeError("Assinatura digital inválida ou editor não reconhecido. "
                           "Instalação bloqueada por segurança.")
    return signer


def download_and_open(app_id: str, notify=None) -> str:
    """Baixa, verifica e abre o instalador original; a instalação fica a cargo do fornecedor."""
    if os.name != "nt":
        raise OSError("Os instaladores são exclusivos para Windows.")
    if app_id not in CATALOG:
        raise ValueError("Aplicativo não cadastrado.")
    app = CATALOG[app_id]
    if not _safe_https(app["url"], app["hosts"]):
        raise ValueError("URL de download não autorizada.")
    notify = notify or (lambda _message: None)

    folder = ROOT / app_id
    folder.mkdir(parents=True, exist_ok=True)
    executable = folder / app["filename"]
    # Uma extensao .exe permite a verificacao Authenticode pelo Windows,
    # inclusive em edicoes Enterprise sem associacao para arquivos .download.
    part = folder / (Path(app["filename"]).stem + ".parcial.exe")
    notify(f"Baixando {app['name']} do fornecedor oficial...")
    opener = urllib.request.build_opener(_OfficialRedirects(app["hosts"]))
    request = urllib.request.Request(app["url"], headers={"User-Agent": "CallasOptimizer/8.9.7"})
    maximum = 300 * 1024 * 1024
    size = 0
    digest = hashlib.sha256()
    try:
        with opener.open(request, timeout=45) as response:
            if not _safe_https(response.geturl(), app["hosts"]):
                raise RuntimeError("URL final do download não é do fornecedor oficial.")
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > maximum:
                raise RuntimeError("Arquivo maior que o limite de segurança.")
            with part.open("wb") as output:
                while True:
                    block = response.read(256 * 1024)
                    if not block:
                        break
                    if size == 0 and not block.startswith(b"MZ"):
                        raise RuntimeError("O servidor não entregou um instalador Windows.")
                    size += len(block)
                    if size > maximum:
                        raise RuntimeError("Download excedeu o tamanho permitido.")
                    digest.update(block)
                    output.write(block)
                    if size % (5 * 1024 * 1024) < len(block):
                        notify(f"{app['name']}: {size // 1048576} MB recebidos...")
        if size < 100 * 1024:
            raise RuntimeError("O download é pequeno demais para um instalador válido.")
        notify("Validando a assinatura digital do fornecedor...")
        signer = verify_authenticode(part, app["publisher"])
        os.replace(part, executable)
        notify("Arquivo assinado e verificado. Abrindo instalador...")
        subprocess.Popen([str(executable)], cwd=str(folder), shell=False)
        return (f"O instalador oficial do {app['name']} foi aberto.\n"
                "Siga as etapas apresentadas pelo próprio fabricante.\n"
                f"Editor verificado: {signer}\nSHA-256: {digest.hexdigest()}")
    finally:
        try:
            part.unlink(missing_ok=True)
        except OSError:
            pass
