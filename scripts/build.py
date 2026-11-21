#!/usr/bin/env python3
"""Compila executavel Win64 standalone com clang/lld-link, no CRT Microsoft."""
from pathlib import Path
import subprocess, hashlib, shutil, sys
root = Path(__file__).resolve().parents[1]
src = root/'src'
items = [
 ('engine','Callas_Optimizer_V8_8_GUI_Engine.bat'),
 ('brave','install_brave.ps1'),
 ('nvidia','install_nvidia.ps1'),
 ('ext','extensions.ps1'),
 ('undo','undo_extensions.ps1'),
 ('updater','updater.ps1'),
]
assets=root/'scripts'/'assets.c'
with assets.open('w') as f:
 f.write('typedef unsigned char BYTE;\ntypedef unsigned int DWORD;\n')
 for sym,n in items:
  data=(src/n).read_bytes()
  f.write('const BYTE asset_'+sym+'[] = {\n')
  for k in range(0,len(data),24): f.write('  '+','.join(str(b) for b in data[k:k+24])+',\n')
  f.write('};\nconst DWORD asset_'+sym+'_size = '+str(len(data))+';\n')
clang=shutil.which('clang')
linker=shutil.which('lld-link')
if not clang or not linker: sys.exit('clang e lld-link sao necessarios')
for srcpath,obj in [(src/'app.c',root/'scripts'/'app.obj'),(assets,root/'scripts'/'assets.obj')]:
 subprocess.run([clang,'-target','x86_64-pc-windows-msvc','-fms-extensions','-ffreestanding','-fno-builtin','-fno-stack-protector','-c',str(srcpath),'-o',str(obj)],check=True)
root.joinpath('dist').mkdir(exist_ok=True)
exe=root/'dist'/'Callas_Optimizer_Windows_x64.exe'
cmd=[linker,'/subsystem:windows','/entry:mainCRTStartup','/nodefaultlib','/machine:x64','/out:'+str(exe),str(root/'scripts'/'app.obj'),str(root/'scripts'/'assets.obj')]
cmd+=list(map(str,(root/'importlibs').glob('*.lib')))
subprocess.run(cmd,check=True)
h=hashlib.sha256(exe.read_bytes()).hexdigest()
(root/'dist'/'SHA256SUMS.txt').write_text(f'{h}  {exe.name}\n')
print('Executavel:',exe,exe.stat().st_size,'bytes\nSHA256:',h)
