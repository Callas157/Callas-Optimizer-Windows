from pathlib import Path
import re, sys
root=Path(__file__).resolve().parents[1]
tag=sys.argv[1] if len(sys.argv)>1 else ''
if not re.fullmatch(r'v\d+\.\d+\.\d+',tag):sys.exit('Tag invalida: '+tag)
s=(root/'src'/'app.c').read_text()
ps=(root/'src'/'updater.ps1').read_text()
ver=tag[1:]
if f'CurrentVersion {ver}' not in s or f'VERSAO   {ver}' not in s:
 sys.exit('Versao do app.c nao corresponde a tag: '+tag)
if "Callas157/Callas-Optimizer-Windows" not in ps:
 sys.exit('Repositorio de atualizacao diferente do projeto')
print('Versao validada:',tag)
