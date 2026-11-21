#!/usr/bin/env python3
"""Garante que versao da GUI, comando de update, VERSION e tag coincidam."""
from pathlib import Path
import re,sys
root=Path(__file__).resolve().parents[1]
tag=sys.argv[1] if len(sys.argv)>1 else ''
if not re.fullmatch(r'v\d+\.\d+\.\d+',tag):sys.exit('Tag invalida: '+tag)
ver=(root/'VERSION').read_text().strip()
if tag!='v'+ver:sys.exit(f'Tag {tag} nao corresponde a VERSION={ver}')
app=(root/'src/app.c').read_text()
ps=(root/'src/updater.ps1').read_text()
if f'VERSAO   {ver}' not in app or f'-CurrentVersion {ver}' not in app:
 sys.exit('Versao local no app.c nao corresponde a VERSION')
if 'Callas157/Callas-Optimizer-Windows' not in ps:
 sys.exit('Updater nao esta ligado ao repositorio oficial correto')
if '-StatusFile ' not in app or 'poll_update_install' not in app:
 sys.exit('GUI sem handshake de instalacao')
print('Versionamento validado:',tag)
