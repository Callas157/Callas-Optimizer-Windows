#!/usr/bin/env python3
"""Valida PE e publica SHA256 dos dois executaveis."""
from pathlib import Path
import hashlib, struct
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
targets=[(dist/'Callas_Optimizer_Windows_x64.exe',False),
         (dist/'Callas_Optimizer_Setup_x64.exe',True)]
lines=[]
for path,setup in targets:
    data=path.read_bytes()
    assert 10_240 <= len(data) <= 250*1024*1024
    assert data[:2] == b'MZ'
    pos=struct.unpack_from('<I',data,0x3c)[0]
    assert data[pos:pos+4] == b'PE\0\0'
    machine=struct.unpack_from('<H',data,pos+4)[0]
    assert machine in ({0x8664,0x14c} if setup else {0x8664})
    lines.append(f"{hashlib.sha256(data).hexdigest()}  {path.name}")
(dist/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='ascii')
print('Portatil e Setup validados')
