"""Limpeza seletiva de temporarios, sem seguir links e com cancelamento.

Nao apaga Prefetch, logs do Windows, pastas do aplicativo ou caches de navegadores.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import stat
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
    recycle_bin: str = "não selecionada"
    recycle_error: str = ""
    icon_cache: str = "não selecionado"
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
        if not p.is_absolute() or p.anchor.startswith("\\\\"):
            continue
        if p.name.lower() != "temp" and p != Path(tempfile.gettempdir()):
            continue
        if p.parent == p or len(p.parts) < 2:
            continue
        try:
            if not is_plain_directory(p):
                continue
            resolved = p.resolve(strict=True)
        except OSError:
            continue
        if resolved not in result:
            result.append(resolved)
    return result


def is_plain_directory(path: Path) -> bool:
    info = path.stat(follow_symlinks=False)
    return stat.S_ISDIR(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400


def nvidia_dxcache_folders() -> list[Path]:
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local.is_absolute() or local.anchor.startswith("\\\\"):
        return []
    paths = (
        (local.parent, (local.name, "NVIDIA", "DXCache")),
        (local.parent, ("LocalLow", "NVIDIA", "DXCache")),
        (local.parent, ("LocalLow", "NVIDIA", "PerDriverVersion", "DXCache")),
    )
    result = []
    for folder, parts in paths:
        try:
            for part in parts:
                folder /= part
                if not is_plain_directory(folder):
                    break
            else:
                result.append(folder)
        except OSError:
            continue
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
            if not is_plain_directory(folder):
                stats.skipped += 1
                return
            with os.scandir(folder) as entries:
                children = list(entries)
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

    dxcache = set(nvidia_dxcache_folders()) if any(p.name.lower() == "dxcache" for p in roots) else set()
    for root in roots:
        if cancelled.is_set():
            stats.cancelled = True
            break
        # Evita exclusao por raiz trocada/symlink.
        if (not root.is_absolute() or root.anchor.startswith("\\\\") or
                (root.name.lower() != "temp" and root not in dxcache)):
            stats.skipped += 1
            continue
        before = stats.files, stats.folders, stats.skipped
        emit(f"Limpando: {root}")
        visit(root)
        emit(f"{root}: {stats.files - before[0]} arquivo(s) e {stats.folders - before[1]} "
             f"pasta(s) vazia(s) removidos, {stats.skipped - before[2]} item(ns) ignorado(s).")
    return stats


class RecycleBinInfo(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("bytes_used", ctypes.c_longlong),
                ("items", ctypes.c_longlong)]


def recycle_bin_items() -> int:
    if os.name != "nt":
        raise RuntimeError("A Lixeira está disponível no Windows.")
    info = RecycleBinInfo(size=ctypes.sizeof(RecycleBinInfo))
    query = ctypes.windll.shell32.SHQueryRecycleBinW
    query.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(RecycleBinInfo)]
    query.restype = wintypes.LONG
    result = query(None, ctypes.byref(info))
    if result != 0:
        raise OSError(f"Falha ao consultar a Lixeira (HRESULT 0x{result & 0xFFFFFFFF:08X}).")
    return info.items


def empty_recycle_bin() -> str:
    if recycle_bin_items() == 0:
        return "já vazia"
    # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    empty = ctypes.windll.shell32.SHEmptyRecycleBinW
    empty.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.DWORD]
    empty.restype = wintypes.LONG
    result = empty(None, None, 0x00000007)
    if result != 0:
        try:
            remaining = recycle_bin_items()
        except OSError:
            remaining = None
        if remaining != 0:
            raise OSError(f"Falha ao esvaziar a Lixeira (HRESULT 0x{result & 0xFFFFFFFF:08X}).")
    return "esvaziada"


def refresh_shell_icons() -> None:
    if os.name != "nt":
        raise OSError("A atualização de ícones está disponível no Windows.")
    notify = ctypes.windll.shell32.SHChangeNotify
    notify.argtypes = [wintypes.LONG, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p]
    notify.restype = None
    notify(0x08000000, 0, None, None)  # SHCNE_ASSOCCHANGED | SHCNF_IDLIST


def clear_icon_cache() -> tuple[int, int]:
    """Remove somente bancos de ícones do perfil atual e notifica o Explorer."""
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local.is_absolute() or local.anchor.startswith("\\\\") or not is_plain_directory(local):
        raise OSError("A pasta de cache do usuário não está disponível.")
    candidates = [local / "IconCache.db"]
    explorer = local
    for component in ("Microsoft", "Windows", "Explorer"):
        explorer /= component
        try:
            if not is_plain_directory(explorer):
                break
        except FileNotFoundError:
            break
    else:
        candidates.extend(explorer.glob("iconcache*.db"))

    removed = skipped = 0
    for candidate in candidates:
        try:
            info = candidate.stat(follow_symlinks=False)
            if not stat.S_ISREG(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                skipped += 1
                continue
            candidate.unlink()
            removed += 1
        except FileNotFoundError:
            continue
        except OSError:
            skipped += 1
    refresh_shell_icons()
    return removed, skipped
