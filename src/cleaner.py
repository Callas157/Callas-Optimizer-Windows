"""Limpeza seletiva de temporarios, sem seguir links e com cancelamento.

Nao apaga Prefetch, logs do Windows, pastas do aplicativo ou caches de navegadores.
"""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import tempfile
import threading
from dataclasses import dataclass
from typing import Callable


@dataclass
class CleanStats:
    files: int = 0
    bytes_freed: int = 0
    skipped: int = 0
    folders: int = 0
    recycle_bin: bool = False
    cancelled: bool = False


def format_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return "0 B"


def known_temp_folders(include_windows: bool = False) -> list[Path]:
    """Usa exclusivamente diretorios de temp fornecidos pelo Windows.

    Ignora caminhos relativos, UNC, simbolicos e raizes de unidade.
    """
    roots = [Path(tempfile.gettempdir()), Path(os.environ.get("LOCALAPPDATA", "")) / "Temp"]
    if include_windows and os.name == "nt":
        roots.append(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp")
    result: list[Path] = []
    for p in roots:
        if not p.is_absolute() or p.is_symlink() or not p.is_dir():
            continue
        if p.name.lower() != "temp" and p != Path(tempfile.gettempdir()):
            continue
        if p.parent == p or len(p.parts) < 2:
            continue
        resolved = p.resolve()
        if resolved not in result:
            result.append(resolved)
    return result


def clean_folders(
    roots: list[Path],
    cancelled: threading.Event,
    on_progress: Callable[[str], None] | None = None,
) -> CleanStats:
    """Apaga conteudo dos diretorios aprovados, preservando as raizes.

    Recursao sem seguir reparse points. Arquivos bloqueados sao ignorados.
    """
    stats = CleanStats()
    def emit(message: str) -> None:
        if on_progress:
            on_progress(message)

    def visit(folder: Path) -> None:
        if cancelled.is_set():
            stats.cancelled = True
            return
        try:
            children = list(os.scandir(folder))
        except OSError:
            stats.skipped += 1
            return
        for entry in children:
            if cancelled.is_set():
                stats.cancelled = True
                return
            try:
                # Links e reparse points jamais sao percorridos nem apagados.
                attrs = entry.stat(follow_symlinks=False)
                if entry.is_symlink() or (getattr(attrs, "st_file_attributes", 0) & 0x400):
                    stats.skipped += 1
                    continue
                if entry.is_dir(follow_symlinks=False):
                    visit(Path(entry.path))
                    try:
                        os.rmdir(entry.path)
                        stats.folders += 1
                    except OSError:
                        stats.skipped += 1
                elif entry.is_file(follow_symlinks=False):
                    size = attrs.st_size
                    os.unlink(entry.path)
                    stats.files += 1
                    stats.bytes_freed += size
                    if stats.files % 35 == 0:
                        emit(f"{stats.files} arquivos removidos • {format_size(stats.bytes_freed)} liberados")
                else:
                    stats.skipped += 1
            except OSError:
                stats.skipped += 1

    for root in roots:
        if cancelled.is_set():
            stats.cancelled = True
            break
        # Evita exclusao por raiz trocada/symlink.
        if (not root.is_dir() or root.is_symlink()
                or (getattr(root.stat(follow_symlinks=False), "st_file_attributes", 0) & 0x400)
                or root.name.lower() != "temp"):
            stats.skipped += 1
            continue
        emit(f"Limpando: {root}")
        visit(root)
    return stats


def empty_recycle_bin() -> None:
    if os.name != "nt":
        raise RuntimeError("Lixeira do Windows so pode ser limpa no Windows.")
    # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000007)
    if result != 0:
        raise OSError(f"Falha ao esvaziar lixeira (HRESULT {result:#x}).")
