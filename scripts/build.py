#!/usr/bin/env python3
"""Gera Callas Optimizer Windows x64 via PyInstaller em runner Windows.

Apenas instalador: pasta do app com DLLs (onedir), evitando extracao _MEI a cada abertura.
"""
from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if os.name != 'nt':
    raise SystemExit('O executavel Windows deve ser compilado em Windows x64 (GitHub Actions).')

icon_b64 = ROOT / 'assets/icons/callas.ico.b64'
icon_file = ROOT / 'assets/icons/callas.ico'
icon_file.write_bytes(base64.b64decode(icon_b64.read_text(encoding='ascii')))
assert icon_file.read_bytes()[:4] == b'\x00\x00\x01\x00', 'Arquivo ICO invalido'

source = ROOT / 'src'
args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
        '--onedir', '--contents-directory', '_internal', '--windowed', '--noupx',
        '--name', 'Callas_Optimizer_Windows_x64', '--icon', str(icon_file),
        '--hidden-import', 'PySide6.QtSvg',
        '--distpath', str(ROOT / 'dist'),
        '--workpath', str(ROOT / 'build'),
        '--specpath', str(ROOT / 'build')]
for file in ('updater.ps1', 'install_brave.ps1',
             'install_nvidia.ps1', 'extensions.ps1', 'undo_extensions.ps1'):
    args += ['--add-data', f'{source / file}{os.pathsep}runtime']
args += ['--add-data', f'{ROOT / "assets/icons"}{os.pathsep}assets/icons']
args += [str(source / 'app.py')]
subprocess.run(args, cwd=ROOT, check=True)
exe = ROOT / 'dist/Callas_Optimizer_Windows_x64/Callas_Optimizer_Windows_x64.exe'
assert (exe.parent / '_internal' / 'python312.dll').is_file(), 'python312.dll nao incluido no pacote'
assert (exe.parent / '_internal' / 'PySide6').is_dir(), 'Qt nao incluido no pacote'
size = exe.stat().st_size
if size > 100 * 1024 * 1024:
    raise SystemExit(f'EXE de {size} bytes ultrapassa o limite de 100 MiB do updater da versao 8.9.1.')
sha = hashlib.sha256(exe.read_bytes()).hexdigest()
print(f'PE64 Windows: {exe.name} ({size} bytes) SHA256={sha}')
