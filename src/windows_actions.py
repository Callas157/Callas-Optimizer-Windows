"""Ações Windows da central Callas Optimizer.

Python é o motor de decisão e de backup. Os comandos nativos (DISM, SFC,
netsh, PowerShell, Registro) são executados sem shell=True.
"""
from __future__ import annotations
import base64
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request
import webbrowser
import winreg

from extra_installers import (
    _system_program, official_https_opener, powershell_env, powershell_path,
    verify_authenticode, winget_path,
)

HOME = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CallasTeck"
BACKUP = HOME / "actions_backup.json"
LOG = HOME / "acoes.log"
WINUTIL_VERSION = "26.11.13"
WINUTIL_URL = f"https://github.com/ChrisTitusTech/winutil/releases/download/{WINUTIL_VERSION}/winutil.ps1"
WINUTIL_SHA256 = "e9d05a59d564b4fbb61fcfa1a594504a0f81e8d27c787119e72a99b57ddbe66d"
WINUTIL_MAX_BYTES = 4 * 1024 * 1024
GAME_BAR = r"Software\Microsoft\GameBar"
WINDOWS_UPDATE = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
DATA_COLLECTION = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
CLASSIC_MENU = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
GAME_SERVICES = ("SysMain", "WSearch")
UPDATE_SERVICES = ("wuauserv", "BITS", "DoSvc", "UsoSvc")
REGISTRY_SETTINGS = {
    ("CU", GAME_BAR, "AutoGameModeEnabled"): winreg.REG_DWORD,
    ("LM", WINDOWS_UPDATE, "NoAutoUpdate"): winreg.REG_DWORD,
    ("LM", WINDOWS_UPDATE, "AUOptions"): winreg.REG_DWORD,
    ("LM", DATA_COLLECTION, "AllowTelemetry"): winreg.REG_DWORD,
    ("CU", CLASSIC_MENU, ""): winreg.REG_SZ,
}

# (id, rota, título, descrição, administrador, alerta)
ROWS = [
 ("gamer_on","gamer","Ativar Modo Jogo","Define preferência de jogos do Windows.",False,""),
 ("gamer_off","gamer","Restaurar Modo Jogo","Retorna à preferência anterior.",False,""),
 ("power_on","gamer","Alto desempenho","Salva e altera plano de energia.",True,""),
 ("power_off","gamer","Restaurar energia","Retorna ao plano salvo.",True,""),
 ("gamer_services_off","gamer","Desativar SysMain e Pesquisa","Salva a inicialização dos serviços.",True,"Interrompe indexação."),
 ("gamer_services_on","gamer","Restaurar serviços","Retorna ao modo original de inicialização.",True,""),
 ("hiber_off","gamer","Desativar hibernação","Afeta também a Inicialização Rápida.",True,""),
 ("hiber_on","gamer","Restaurar hibernação","Reativa caso tenha sido desligada aqui.",True,""),
 ("edge_uninstall","edge","Tentar remover Edge","Usa o desinstalador nativo, se disponível.",True,"Alguns Windows bloqueiam a remoção."),
 ("edge_restore","edge","Restaurar Edge","Usa WinGet quando disponível.",False,""),
 ("wu_notify","windows_update","Notificar antes de baixar","Configura política do Windows Update.",True,""),
 ("wu_pause","windows_update","Desativar atualização automática","Altera política, sem alterar serviços.",True,"Reduz a proteção de segurança."),
 ("wu_services_off","windows_update","Suspender serviços de atualização","Salva o modo de inicialização.",True,"Pode impedir Store e atualizações."),
 ("wu_restore","windows_update","Restaurar Windows Update","Recupera políticas e serviços.",True,""),
 ("flush_dns","network","Limpar cache DNS","Executa ipconfig /flushdns.",False,""),
 ("reset_winsock","network","Redefinir Winsock","Redefine rede, pode exigir reinício.",True,"A rede pode cair."),
 ("dns_cloudflare","network","DNS Cloudflare","Aplica 1.1.1.1 e 1.0.0.1 nas interfaces ativas.",True,""),
 ("dns_auto","network","Restaurar DNS automático","Restabelece DNS fornecido pela rede.",True,""),
 ("telemetry_reduce","privacy","Reduzir telemetria opcional","Define política de dados de diagnóstico.",True,"Limite varia por edição."),
 ("telemetry_restore","privacy","Restaurar telemetria","Restaura valor anterior.",True,""),
 ("repair_dism","repair","Reparar imagem com DISM","Executa DISM /RestoreHealth.",True,""),
 ("repair_sfc","repair","Reparar arquivos com SFC","Executa sfc /scannow.",True,""),
 ("repair_disk","repair","Examinar disco do sistema","Executa chkdsk /scan.",True,""),
 ("classic_on","classic","Ativar menu clássico","Ativa ajuste reversível.",False,"Pode exigir reinício Explorer."),
 ("classic_off","classic","Restaurar menu moderno","Reverte ajuste registrado.",False,""),
 ("shutdown_15","shutdown","Desligar em 15 minutos","Agenda desligamento.",False,"Salve seus arquivos."),
 ("shutdown_30","shutdown","Desligar em 30 minutos","Agenda desligamento.",False,"Salve seus arquivos."),
 ("shutdown_60","shutdown","Desligar em 60 minutos","Agenda desligamento.",False,"Salve seus arquivos."),
 ("shutdown_cancel","shutdown","Cancelar desligamento","Cancela um desligamento pendente.",False,""),
 ("winutil_open","winutil","Abrir WinUtil oficial","Baixa a versão verificada e abre a interface do WinUtil.",True,
  "As opções que você escolher no WinUtil podem alterar o sistema."),
 ("restore_point","restore_point","Criar ponto de restauração","Usa ferramenta oficial Windows.",True,""),
 ("restore_reg","restore","Restaurar ajustes do Registro","Usa apenas backups feitos pela central.",True,""),
 ("restore_services","restore","Restaurar serviços","Recupera modos de inicialização guardados.",True,""),
 ("restore_all","restore","Restaurar ajustes salvos","Registro, serviços e energia (quando salvos).",True,"")
]
ACTIONS = {r[0]: {"id":r[0],"route":r[1],"name":r[2],"description":r[3],"admin":r[4],"warning":r[5]} for r in ROWS}
BY_ROUTE = {route:[ACTIONS[r[0]] for r in ROWS if r[1]==route] for route in {r[1] for r in ROWS}}


def admin():
    return os.name=="nt" and bool(ctypes.windll.shell32.IsUserAnAdmin())


def cmd(*argv, optional=False, env=None):
    if os.name!="nt": raise OSError("Ação exclusiva do Windows.")
    if not Path(argv[0]).is_absolute():
        argv = (str(_system_program(argv[0])), *argv[1:])
    proc=subprocess.run(argv,shell=False,capture_output=True,text=True,errors="replace",env=env,
                        timeout=1800,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    output=(proc.stdout+"\n"+proc.stderr).strip()
    if proc.returncode and not optional:
        raise RuntimeError(f"{argv[0]} retornou {proc.returncode}.\n{output[-900:]}")
    return output or f"Concluído (código {proc.returncode})."


def ps(source):
    encoded=base64.b64encode(source.encode("utf-16le")).decode("ascii")
    return cmd(str(powershell_path()),"-NoLogo","-NoProfile","-NonInteractive","-EncodedCommand",encoded,
               env=powershell_env())


def load():
    try: return json.loads(BACKUP.read_text(encoding="utf-8"))
    except (OSError,ValueError): return {"reg":{},"svc":{},"power":None,"hiber":False}


def save(data):
    HOME.mkdir(parents=True,exist_ok=True)
    tmp=BACKUP.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(tmp,BACKUP)


def setreg(hive,path,name,value,kind=winreg.REG_DWORD):
    root=winreg.HKEY_CURRENT_USER if hive=="CU" else winreg.HKEY_LOCAL_MACHINE
    st=load()
    keyid="|".join((hive,path,name))
    if keyid not in st["reg"]:
        try:
            with winreg.OpenKey(root,path,0,winreg.KEY_READ) as handle:
                prev,typ=winreg.QueryValueEx(handle,name)
            old={"found":True,"value":prev,"type":typ}
        except FileNotFoundError:
            old={"found":False}
        st["reg"][keyid]={"hive":hive,"path":path,"name":name,**old}
        save(st)
    with winreg.CreateKeyEx(root,path,0,winreg.KEY_SET_VALUE) as handle:
        winreg.SetValueEx(handle,name,0,kind,value)
    return "Política aplicada. Valor original guardado."


def restore_reg(prefix=""):
    st=load();n=0
    for keyid,old in list(st["reg"].items()):
        if prefix and not keyid.startswith(prefix): continue
        if not isinstance(old, dict):
            continue
        location = old.get("hive"), old.get("path"), old.get("name")
        if any(not isinstance(part, str) for part in location):
            continue
        kind = REGISTRY_SETTINGS.get(location)
        found = old.get("found")
        if kind is None or keyid != "|".join(location) or type(found) is not bool:
            continue
        value = old.get("value")
        if found and (old.get("type") != kind or
                      (kind == winreg.REG_DWORD and (type(value) is not int or not 0 <= value <= 0xFFFFFFFF)) or
                      (kind == winreg.REG_SZ and not isinstance(value, str))):
            continue
        root=winreg.HKEY_CURRENT_USER if location[0]=="CU" else winreg.HKEY_LOCAL_MACHINE
        try:
            if old["found"]:
                with winreg.CreateKeyEx(root,old["path"],0,winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key,old["name"],0,old["type"],old["value"])
            else:
                try:
                    with winreg.OpenKey(root,old["path"],0,winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key,old["name"])
                except FileNotFoundError:pass
            del st["reg"][keyid];save(st);n+=1
        except OSError:pass
    return f"Registro: {n} restaurados; {len(st['reg'])} pendentes."


def services(names,disable):
    st=load();changed=[]
    for name in names:
        if name not in (*GAME_SERVICES, *UPDATE_SERVICES):
            continue
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services"+"\\"+name) as key:
                startup,_=winreg.QueryValueEx(key,"Start")
        except FileNotFoundError:continue
        if disable:
            if name not in st["svc"]:
                st["svc"][name]=startup;save(st)
            cmd("sc.exe","stop",name,optional=True)
            cmd("sc.exe","config",name,"start=","disabled")
            changed.append(name)
        elif name in st["svc"]:
            startup = st["svc"][name]
            mode = {2:"auto",3:"demand",4:"disabled"}.get(startup) if type(startup) is int else None
            if not mode:continue
            cmd("sc.exe","config",name,"start=",mode)
            del st["svc"][name];save(st);changed.append(name)
    return "Serviços modificados: "+(", ".join(changed) or "nenhum")


def energy(enable):
    st=load()
    if enable:
        if not st["power"]:
            found=re.search(r"[0-9A-Fa-f]{8}-(?:[0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12}",cmd("powercfg.exe","/getactivescheme"))
            if not found:raise RuntimeError("Não consegui guardar o plano de energia.")
            st["power"]=found.group();save(st)
        return cmd("powercfg.exe","/setactive","SCHEME_MIN")
    if not st["power"]:return "Não havia plano anterior salvo."
    if not isinstance(st["power"], str) or not re.fullmatch(r"[0-9A-Fa-f]{8}-(?:[0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12}", st["power"]):
        raise ValueError("O identificador do plano de energia salvo é inválido.")
    result=cmd("powercfg.exe","/setactive",st["power"])
    st["power"]=None;save(st);return result


def hibernate(enable):
    st=load()
    if enable and not st["hiber"]:return "A central não havia desativado hibernação."
    r=cmd("powercfg.exe","/hibernate","on" if enable else "off")
    st["hiber"]=not enable;save(st);return r


def edge(uninstall):
    if uninstall:
        location=Path(os.environ.get("PROGRAMFILES(X86)",r"C:\Program Files (x86)"))/"Microsoft/Edge/Application"
        found=sorted(location.glob("*/Installer/setup.exe"),reverse=True) if location.exists() else []
        if not found:raise RuntimeError("Desinstalador Edge não encontrado ou protegido nesta edição.")
        verify_authenticode(found[0], r"Microsoft Corporation")
        return cmd(str(found[0]),"--uninstall","--system-level","--verbose-logging","--force-uninstall")
    winget=winget_path()
    if winget.is_file():return cmd(str(winget),"install","--id","Microsoft.Edge","--exact","--source","winget",
                         "--accept-package-agreements","--accept-source-agreements")
    webbrowser.open("https://www.microsoft.com/edge")
    return "Sem WinGet. Página oficial do Edge aberta para instalação."


def open_winutil() -> str:
    request = urllib.request.Request(WINUTIL_URL, headers={"User-Agent": "CallasOptima"})
    opener = official_https_opener({"github.com", "release-assets.githubusercontent.com",
                                     "objects.githubusercontent.com"})
    with opener.open(request, timeout=30) as response:
        data = response.read(WINUTIL_MAX_BYTES + 1)
    if len(data) > WINUTIL_MAX_BYTES or hashlib.sha256(data).hexdigest() != WINUTIL_SHA256:
        raise RuntimeError("O arquivo do WinUtil não corresponde ao SHA-256 da versão verificada.")

    # A ferramenta oficial é PowerShell. Envia os bytes verificados diretamente
    # ao processo em vez de executar um arquivo que possa ser trocado no disco.
    command = (
        "$reader=[IO.StreamReader]::new([Console]::OpenStandardInput(), [Text.Encoding]::UTF8); "
        "$source=$reader.ReadToEnd(); $reader.Dispose(); & ([ScriptBlock]::Create($source))"
    )
    shell = powershell_path()
    process = subprocess.Popen(
        [str(shell), "-NoLogo", "-NoProfile", "-STA", "-Command", command],
        cwd=shell.parent, env=powershell_env(), stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        with process.stdin as source:
            source.write(data)
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        return f"WinUtil {WINUTIL_VERSION} iniciado."
    except BrokenPipeError as exc:
        raise RuntimeError("O PowerShell encerrou antes de iniciar o WinUtil.") from exc
    raise RuntimeError(f"O WinUtil encerrou durante a inicialização (código {process.returncode}).")


def shutdown(minutes):
    if minutes is None:return cmd("shutdown.exe","/a")
    cmd("shutdown.exe","/a",optional=True)
    return cmd("shutdown.exe","/s","/t",str(minutes*60))


def execute(action_id):
    if action_id not in ACTIONS:raise ValueError("Ação inexistente.")
    if os.name!="nt":raise OSError("Requer Windows.")
    if ACTIONS[action_id]["admin"] and not admin():
        raise PermissionError("Permissão UAC de administrador necessária.")
    gb, wu, dc, cl = GAME_BAR, WINDOWS_UPDATE, DATA_COLLECTION, CLASSIC_MENU
    sg, sw = GAME_SERVICES, UPDATE_SERVICES
    tasks={
        "gamer_on":lambda:setreg("CU",gb,"AutoGameModeEnabled",1),
        "gamer_off":lambda:restore_reg("CU|"+gb),
        "power_on":lambda:energy(True),"power_off":lambda:energy(False),
        "gamer_services_off":lambda:services(sg,True),
        "gamer_services_on":lambda:services(sg,False),
        "hiber_off":lambda:hibernate(False),"hiber_on":lambda:hibernate(True),
        "edge_uninstall":lambda:edge(True),"edge_restore":lambda:edge(False),
        "wu_notify":lambda:setreg("LM",wu,"NoAutoUpdate",0)+" "+setreg("LM",wu,"AUOptions",2),
        "wu_pause":lambda:setreg("LM",wu,"NoAutoUpdate",1),
        "wu_services_off":lambda:services(sw,True),
        "wu_restore":lambda:restore_reg("LM|"+wu)+" "+services(sw,False),
        "flush_dns":lambda:cmd("ipconfig.exe","/flushdns"),
        "reset_winsock":lambda:cmd("netsh.exe","winsock","reset"),
        "dns_cloudflare":lambda:ps("$a=Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; if(!$a){throw 'Sem adaptador ativo'}; $a | ForEach-Object {Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses @('1.1.1.1','1.0.0.1') -ErrorAction Stop}"),
        "dns_auto":lambda:ps("$a=Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; if(!$a){throw 'Sem adaptador ativo'}; $a | ForEach-Object {Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses -ErrorAction Stop}"),
        "telemetry_reduce":lambda:setreg("LM",dc,"AllowTelemetry",0),
        "telemetry_restore":lambda:restore_reg("LM|"+dc),
        "repair_dism":lambda:cmd("dism.exe","/Online","/Cleanup-Image","/RestoreHealth"),
        "repair_sfc":lambda:cmd("sfc.exe","/scannow"),
        "repair_disk":lambda:cmd("chkdsk.exe",os.environ.get("SystemDrive","C:")+"\\","/scan"),
        "classic_on":lambda:setreg("CU",cl,"","",winreg.REG_SZ),
        "classic_off":lambda:restore_reg("CU|"+cl),
        "shutdown_15":lambda:shutdown(15),"shutdown_30":lambda:shutdown(30),
        "shutdown_60":lambda:shutdown(60),"shutdown_cancel":lambda:shutdown(None),
        "winutil_open":open_winutil,
        "restore_point":lambda:ps("Checkpoint-Computer -Description 'Callas Optimizer' -RestorePointType MODIFY_SETTINGS -ErrorAction Stop"),
        "restore_reg":lambda:restore_reg(),
        "restore_services":lambda:services(tuple(load()["svc"]),False),
        "restore_all":lambda:restore_reg()+"\n"+services(tuple(load()["svc"]),False)+"\n"+energy(False),
    }
    result=tasks[action_id]()
    HOME.mkdir(exist_ok=True,parents=True)
    with LOG.open("a",encoding="utf-8") as f:
        f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ")+action_id+" "+result[:2000]+"\n")
    return result


def worker(action_id,filename):
    HOME.mkdir(exist_ok=True,parents=True)
    if not re.fullmatch(r"acao-[a-f0-9]{32}\.json",filename):return 2
    try: result={"ok":True,"message":execute(action_id)[-5000:]}
    except Exception as e:result={"ok":False,"message":str(e)}
    dest=HOME/filename;tmp=dest.with_suffix(".tmp")
    tmp.write_text(json.dumps(result,ensure_ascii=False),encoding="utf-8")
    os.replace(tmp,dest)
    return 0 if result["ok"] else 1
