#!/usr/bin/env python3
"""Bloqueia Release de versao incoerente entre tag, GUI, arquivo e repo."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
tag = sys.argv[1] if len(sys.argv) > 1 else ''
if not re.fullmatch(r'v\d+\.\d+\.\d+', tag):
    sys.exit('Tag invalida: ' + tag)
version = (root / 'VERSION').read_text().strip()
if tag != 'v' + version:
    sys.exit('Tag divergente de VERSION')
app = (root / 'src/app.py').read_text(encoding='utf-8')
updater = (root / 'src/updater.ps1').read_text(encoding='utf-8')
if not re.search(r'^APP_VERSION = "' + re.escape(version) + r'"$', app, re.MULTILINE):
    sys.exit('GUI com versao diferente')
if "Callas157/Callas-Optimizer-Windows" not in updater:
    sys.exit('Updater apontando para repo errado')
if 'Callas157/arch-install' in updater:
    sys.exit('Referencia indevida ao projeto Linux')
print('Versionamento, GUI e repositorio validados:', tag)
