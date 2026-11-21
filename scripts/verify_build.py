#!/usr/bin/env python3
"""Confere formato PE64, arquitetura e hash antes de distribuir no GitHub."""
from pathlib import Path
import hashlib,struct
root=Path(__file__).resolve().parents[1]
exe=root/'dist/Callas_Optimizer_Windows_x64.exe'
b=exe.read_bytes()
assert len(b)>=10240 and b[:2]==b'MZ','EXE MZ invalido'
off=struct.unpack_from('<I',b,0x3c)[0]
assert off+26<len(b) and b[off:off+4]==b'PE\0\0','Cabecalho PE invalido'
assert struct.unpack_from('<H',b,off+4)[0]==0x8664,'Nao e PE64 x86-64'
assert struct.unpack_from('<H',b,off+24)[0]==0x20b,'Nao e PE32+'
h=hashlib.sha256(b).hexdigest()
assert (root/'dist/SHA256SUMS.txt').read_text().strip()==f'{h}  {exe.name}','SHA256SUMS incorreto'
print('PE64 e SHA256 conferidos:',len(b),'bytes')
