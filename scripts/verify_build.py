#!/usr/bin/env python3
"""Confere PE64, SHA-256 e limite aceito por clientes antigos."""
from pathlib import Path
import hashlib
import struct
root = Path(__file__).resolve().parents[1]
exe = root / 'dist/Callas_Optimizer_Windows_x64.exe'
b = exe.read_bytes()
assert 10_240 <= len(b) <= 100 * 1024 * 1024, 'Tamanho de EXE invalido para updater antigo'
assert b[:2] == b'MZ', 'Cabecalho DOS invalido'
off = struct.unpack_from('<I', b, 0x3c)[0]
assert off + 26 < len(b) and b[off:off+4] == b'PE\0\0', 'Cabecalho PE invalido'
assert struct.unpack_from('<H', b, off+4)[0] == 0x8664, 'Nao e Windows x64'
assert struct.unpack_from('<H', b, off+24)[0] == 0x20b, 'Nao e PE32+'
sha = hashlib.sha256(b).hexdigest()
assert (root / 'dist/SHA256SUMS.txt').read_text().strip() == f'{sha}  {exe.name}', 'SHA256 divergente'
print('PE x64, tamanho compativel, SHA256 validados:', len(b))
