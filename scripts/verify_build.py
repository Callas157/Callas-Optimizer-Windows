#!/usr/bin/env python3
"""Valida PE do aplicativo interno e Setup, publica somente hash do Setup."""
from pathlib import Path
import hashlib
import struct

root = Path(__file__).resolve().parents[1]
dist = root / 'dist'
app = dist / 'Callas_Optimizer_Windows_x64' / 'Callas_Optimizer_Windows_x64.exe'  # interno ao Setup
setup = dist / 'Callas_Optimizer_Setup_x64.exe'
assert (app.parent / '_internal' / 'python312.dll').is_file(), 'Runtime Python 3.12 ausente'
assert (app.parent / '_internal' / 'PySide6').is_dir(), 'Bibliotecas Qt ausentes'  # unico download

for path, installer in ((app, False), (setup, True)):
    data = path.read_bytes()
    assert 10_240 <= len(data) <= 250 * 1024 * 1024, path
    assert data[:2] == b'MZ', path
    pos = struct.unpack_from('<I', data, 0x3C)[0]
    assert 0 < pos < len(data) - 24, path
    assert data[pos:pos+4] == b'PE\0\0', path
    machine = struct.unpack_from('<H', data, pos+4)[0]
    assert machine in ({0x8664, 0x14C} if installer else {0x8664}), path
    if not installer:
        assert b'<requestedExecutionLevel level="requireAdministrator"' in data, 'Manifesto UAC ausente no Callas'

sha = hashlib.sha256(setup.read_bytes()).hexdigest()
(dist / 'SHA256SUMS.txt').write_text(f'{sha}  {setup.name}\n', encoding='ascii')
print('Setup validado. Somente o Setup e o SHA-256 serao publicados.')
