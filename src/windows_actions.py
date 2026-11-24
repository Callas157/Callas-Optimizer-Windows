"""Ações Windows da central Callas Optimizer.

Python é o motor de decisão e de backup. Os comandos nativos (DISM, SFC,
netsh, PowerShell, Registro) são executados sem shell=True.
"""
from __future__ import annotations
import base64
import codecs
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import NamedTemporaryFile
from threading import Event, Timer
import time
import urllib.request
import webbrowser

if sys.platform == "win32":
    import msvcrt
    import winreg

from extra_installers import (
    _ShellExecuteInfo, _system_program, official_https_opener, powershell_env, powershell_path,
    verify_authenticode, winget_path,
)

HOME = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CallasTeck"
BACKUP = HOME / "actions_backup.json"
LOG = HOME / "acoes.log"
REPORT_MESSAGE_LIMIT = 5000
PROFILE_MISMATCH = 3
MAX_SHUTDOWN_MINUTES = 315_360_000 // 60
NO_SHUTDOWN_IN_PROGRESS = 1116
SHUTDOWN_TIMER_KEY = r"Software\Callas\OptimizerWindows\ShutdownTimer"
SHUTDOWN_DEADLINE = "Deadline"
NANOSECONDS_PER_MINUTE = 60_000_000_000
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
REPAIR_PROGRESS = {
    "chkdsk.exe": re.compile(r"\btotal\s*:\s*([0-9]{1,3})\s*%", re.IGNORECASE),
    "dism.exe": re.compile(r"\[[= ]*([0-9]{1,3}(?:[.,][0-9]+)?)\s*%"),
    "sfc.exe": re.compile(r"(?<![0-9.,])([0-9]{1,3})\s*%"),
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
 ("flush_dns","network","Limpar cache DNS","Executa ipconfig /flushdns.",True,""),
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
 ("shutdown_custom","shutdown","Desligamento personalizado","Escolha o tempo em minutos.",False,""),
 ("shutdown_cancel","shutdown","Cancelar desligamento","Cancela um desligamento pendente.",False,""),
 ("winutil_open","winutil","Abrir WinUtil oficial","Baixa a versão verificada e abre a interface do WinUtil.",True,
  "As opções que você escolher no WinUtil podem alterar o sistema."),
 ("restore_point","restore_point","Criar ponto de restauração","Usa ferramenta oficial Windows.",True,""),
 ("restore_reg","restore","Restaurar ajustes do Registro","Usa apenas backups feitos pela central.",True,""),
 ("restore_services","restore","Restaurar serviços","Recupera modos de inicialização guardados.",True,""),
 ("restore_all","restore","Restaurar ajustes salvos","Registro, serviços, energia e hibernação (quando salvos).",True,"")
]
ACTIONS = {r[0]: {"id":r[0],"route":r[1],"name":r[2],"description":r[3],"admin":r[4],"warning":r[5]} for r in ROWS}
BY_ROUTE = {route:[ACTIONS[r[0]] for r in ROWS if r[1]==route] for route in {r[1] for r in ROWS}}


def admin():
    return os.name=="nt" and bool(ctypes.windll.shell32.IsUserAnAdmin())


class ElevatedAction:
    """Inicia o trabalhador com UAC e permite consultar sua saída sem bloquear a interface."""

    def __init__(self, executable, args):
        info = _ShellExecuteInfo()
        info.cbSize = ctypes.sizeof(info)
        info.fMask = 0x40 | 0x100 | 0x400  # NOCLOSEPROCESS | NOASYNC | FLAG_NO_UI
        info.lpVerb = "runas"
        info.lpFile = str(executable)
        info.lpParameters = subprocess.list2cmdline(args)
        info.lpDirectory = str(Path(executable).parent)
        info.nShow = 1
        shell = ctypes.WinDLL("shell32", use_last_error=True)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        ole = ctypes.WinDLL("ole32")
        shell.ShellExecuteExW.argtypes = [ctypes.POINTER(_ShellExecuteInfo)]
        self.wait = kernel.WaitForSingleObject
        self.wait.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.wait.restype = wintypes.DWORD
        self.exit_code = kernel.GetExitCodeProcess
        self.exit_code.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        self.close_handle = kernel.CloseHandle
        self.close_handle.argtypes = [wintypes.HANDLE]
        initialized = ole.CoInitializeEx(None, 0x2) in (0, 1)
        try:
            if not shell.ShellExecuteExW(ctypes.byref(info)):
                raise ctypes.WinError(ctypes.get_last_error())
            if not info.hProcess:
                raise RuntimeError("O Windows não retornou o processo da ferramenta.")
            self.handle = info.hProcess
        finally:
            if initialized:
                ole.CoUninitialize()

    def poll(self):
        state = self.wait(self.handle, 0)
        if state == 258:  # WAIT_TIMEOUT: o processo continua em execução.
            return None
        try:
            if state != 0:
                raise ctypes.WinError(ctypes.get_last_error())
            code = wintypes.DWORD()
            if not self.exit_code(self.handle, ctypes.byref(code)):
                raise ctypes.WinError(ctypes.get_last_error())
            return code.value
        finally:
            self.close_handle(self.handle)


def _output_encoding(data, fallback):
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return "utf-16"
    if data.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"
    if len(data) % 2 == 0 and b"\0" in data[1::2]:
        # O SFC pode escrever UTF-16LE sem marca de ordem dos bytes.
        return "utf-16le"
    return fallback


def _decode_output(data, encoding):
    return data.decode(_output_encoding(data, encoding), errors="replace")


def _stream_output(argv, options, timeout, encoding, pattern, progress):
    # Uma só saída evita que o produtor bloqueie enquanto o outro canal é lido.
    with subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **options) as proc:
        timed_out = Event()

        def expire():
            if proc.poll() is None:
                timed_out.set()
                proc.kill()

        timer = Timer(timeout, expire) if timeout is not None else None
        if timer is not None:
            timer.start()
        try:
            chunk = proc.stdout.read(4)
            decoder = codecs.getincrementaldecoder(_output_encoding(chunk, encoding))(errors="replace")
            output = []
            pending = ""
            last_percent = 0
            while chunk:
                decoded = decoder.decode(chunk)
                output.append(decoded)
                lines = re.split(r"[\r\n]", pending + decoded)
                pending = lines[-1]
                for line in lines:
                    match = pattern.search(line)
                    if match is None:
                        continue
                    value = float(match[1].replace(",", "."))
                    percent = min(int(value), 99)
                    if value <= 100 and percent > last_percent:
                        last_percent = percent
                        progress(percent)
                chunk = proc.stdout.read1(8192)
            output.append(decoder.decode(b"", final=True))
            code = proc.wait()
        except BaseException:
            if proc.poll() is None:
                proc.kill()
            raise
        finally:
            if timer is not None:
                timer.cancel()
                timer.join()
    text = "".join(output)
    if timed_out.is_set():
        raise subprocess.TimeoutExpired(argv, timeout, output=text)
    return code, text


def cmd(*argv, optional=False, env=None, timeout=1800, success_codes=(0,), encoding=None, progress=None):
    if os.name!="nt": raise OSError("Ação exclusiva do Windows.")
    program = Path(argv[0]).name.lower()
    if not Path(argv[0]).is_absolute():
        argv = (str(_system_program(argv[0])), *argv[1:])
    if encoding is None:
        if program == "chkdsk.exe":
            # A saída redirecionada do CHKDSK usa a página de código ANSI do Windows.
            encoding = "mbcs" if sys.platform == "win32" else "cp1252"
        else:
            encoding = "oem" if sys.platform == "win32" else "utf-8"
    options = dict(shell=False, stdin=subprocess.DEVNULL, env=env,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    pattern = REPAIR_PROGRESS.get(program)
    if progress is not None and pattern is not None:
        code, output = _stream_output(argv, options, timeout, encoding, pattern, progress)
    else:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout, **options)
        code = proc.returncode
        output = "\n".join(_decode_output(part, encoding) for part in (proc.stdout, proc.stderr))
    output = output.replace("\r\n", "\n").strip()
    if code not in success_codes and not optional:
        raise RuntimeError(f"{argv[0]} retornou {code}.\n{output[-900:]}")
    return output or f"Concluído (código {code})."


def ps(source):
    script = (
        "[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false); "
        "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue'; "
        "try { & { " + source + " } } catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
    )
    encoded=base64.b64encode(script.encode("utf-16le")).decode("ascii")
    return cmd(str(powershell_path()),"-NoLogo","-NoProfile","-NonInteractive","-EncodedCommand",encoded,
               env=powershell_env(), encoding="utf-8")


def load():
    defaults = {"reg": {}, "svc": {}, "power": None, "hiber": False}
    try:
        data = json.loads(BACKUP.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return defaults
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Não foi possível ler o backup de manutenção: {BACKUP}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"Formato inválido no backup de manutenção: {BACKUP}")
    data = {**defaults, **data}
    if not isinstance(data["reg"], dict) or not isinstance(data["svc"], dict):
        raise RuntimeError(f"Formato inválido no backup de manutenção: {BACKUP}")
    return data


def applied_action_backups() -> set[str]:
    """Identify settings for which this profile still holds a previous value."""
    state = load()
    applied = set()
    registry_actions = {
        "gamer_on": ("CU", GAME_BAR, "AutoGameModeEnabled"),
        "telemetry_reduce": ("LM", DATA_COLLECTION, "AllowTelemetry"),
        "classic_on": ("CU", CLASSIC_MENU, ""),
    }
    for action, location in registry_actions.items():
        if "|".join(location) in state["reg"]:
            applied.add(action)
    if any(service in state["svc"] for service in GAME_SERVICES):
        applied.add("gamer_services_off")
    if state["power"]:
        applied.add("power_on")
    if state["hiber"] is True:
        applied.add("hiber_off")
    return applied


def save(data):
    HOME.mkdir(parents=True,exist_ok=True)
    tmp=BACKUP.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    os.replace(tmp,BACKUP)


def setreg(hive,path,name,value,kind=None):
    if kind is None:
        kind = winreg.REG_DWORD
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
    registry_settings = {
        ("CU", GAME_BAR, "AutoGameModeEnabled"): winreg.REG_DWORD,
        ("LM", WINDOWS_UPDATE, "NoAutoUpdate"): winreg.REG_DWORD,
        ("LM", WINDOWS_UPDATE, "AUOptions"): winreg.REG_DWORD,
        ("LM", DATA_COLLECTION, "AllowTelemetry"): winreg.REG_DWORD,
        ("CU", CLASSIC_MENU, ""): winreg.REG_SZ,
    }
    st=load();n=0
    for keyid,old in list(st["reg"].items()):
        if prefix and not keyid.startswith(prefix): continue
        if not isinstance(old, dict):
            continue
        location = old.get("hive"), old.get("path"), old.get("name")
        if any(not isinstance(part, str) for part in location):
            continue
        kind = registry_settings.get(location)
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
    pending = sum(not prefix or keyid.startswith(prefix) for keyid in st["reg"])
    return f"Registro: {n} restaurados. Pendentes: {pending}."


def services(names, disable):
    st = load()
    changed = []
    failures = []
    for name in names:
        if name not in (*GAME_SERVICES, *UPDATE_SERVICES):
            continue
        if disable:
            if name not in st["svc"]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                        rf"SYSTEM\CurrentControlSet\Services\{name}") as key:
                        startup, _ = winreg.QueryValueEx(key, "Start")
                        delayed = False
                        if startup == 2:
                            try:
                                delayed = winreg.QueryValueEx(key, "DelayedAutoStart")[0] == 1
                            except FileNotFoundError:
                                pass
                except FileNotFoundError:
                    continue
                st["svc"][name] = {"start": startup, "delayed": delayed}
                save(st)
            mode = "disabled"
        elif name in st["svc"]:
            snapshot = st["svc"][name]
            startup = snapshot.get("start") if isinstance(snapshot, dict) else snapshot
            delayed = isinstance(snapshot, dict) and snapshot.get("delayed") is True
            mode = {2:"auto",3:"demand",4:"disabled"}.get(startup) if type(startup) is int else None
            if not mode:continue
            if mode == "auto" and delayed:
                mode = "delayed-auto"
        else:
            continue
        try:
            cmd("sc.exe", "config", name, "start=", mode)
            if disable:
                cmd("sc.exe", "stop", name, optional=True)
            else:
                del st["svc"][name]
                save(st)
            changed.append(name)
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{name}: {exc}")
    summary = "Serviços modificados: " + (", ".join(changed) or "nenhum")
    if failures:
        raise RuntimeError("\n".join([summary, *failures]))
    return summary


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
    st = load()
    if type(st["hiber"]) is not bool:
        raise ValueError("O estado de hibernação salvo é inválido.")
    if enable and not st["hiber"]:
        return "A central não havia desativado a hibernação."
    if not enable and not st["hiber"]:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power") as key:
            enabled, _ = winreg.QueryValueEx(key, "HibernateEnabled")
        if not enabled:
            return "A hibernação já estava desativada."
        st["hiber"] = True
        save(st)
    result = cmd("powercfg.exe", "/hibernate", "on" if enable else "off")
    if enable:
        st["hiber"] = False
        save(st)
    return result


def edge_install_dirs():
    for variable, fallback in (("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                               ("PROGRAMFILES", r"C:\Program Files")):
        yield Path(os.environ.get(variable, fallback)) / "Microsoft" / "Edge" / "Application"


def edge_installed() -> bool:
    return os.name == "nt" and any((location / "msedge.exe").is_file() for location in edge_install_dirs())


def edge(uninstall):
    if uninstall:
        location = next((path for path in edge_install_dirs() if (path / "msedge.exe").is_file()),
                        next(edge_install_dirs()))
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


def _read_shutdown_deadline() -> int | None:
    if sys.platform != "win32":
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, SHUTDOWN_TIMER_KEY) as key:
            value, kind = winreg.QueryValueEx(key, SHUTDOWN_DEADLINE)
            return value if kind == winreg.REG_QWORD else None
    except OSError:
        return None


def _write_shutdown_deadline(deadline: int | None):
    if deadline is None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, SHUTDOWN_TIMER_KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, SHUTDOWN_DEADLINE)
        except FileNotFoundError:
            pass
        return

    # A volatile key survives closing the app and is discarded when Windows unloads the hive.
    reg_option_volatile = 1
    create_key = ctypes.windll.advapi32.RegCreateKeyExW
    create_key.argtypes = (
        wintypes.HKEY, wintypes.LPCWSTR, wintypes.DWORD, wintypes.LPWSTR,
        wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(wintypes.HKEY),
        ctypes.POINTER(wintypes.DWORD),
    )
    create_key.restype = wintypes.LONG
    current_user = wintypes.HKEY(ctypes.c_int32(winreg.HKEY_CURRENT_USER).value)
    key = wintypes.HKEY()
    error = create_key(current_user, SHUTDOWN_TIMER_KEY, 0, None, reg_option_volatile,
                       winreg.KEY_SET_VALUE, None, ctypes.byref(key), None)
    if error:
        raise ctypes.WinError(error)
    try:
        winreg.SetValueEx(key.value, SHUTDOWN_DEADLINE, 0, winreg.REG_QWORD, deadline)
    finally:
        winreg.CloseKey(key.value)


def remaining_shutdown_minutes() -> int | None:
    deadline = _read_shutdown_deadline()
    if deadline is None:
        return None
    remaining = deadline - time.monotonic_ns()
    if 0 < remaining <= MAX_SHUTDOWN_MINUTES * NANOSECONDS_PER_MINUTE:
        return (remaining + NANOSECONDS_PER_MINUTE - 1) // NANOSECONDS_PER_MINUTE
    return None


def abort_shutdown():
    cmd("shutdown.exe", "/a", success_codes=(0, NO_SHUTDOWN_IN_PROGRESS))


def shutdown(minutes: int | None):
    if minutes is not None and (type(minutes) is not int or not 1 <= minutes <= MAX_SHUTDOWN_MINUTES):
        raise ValueError(f"Escolha entre 1 e {MAX_SHUTDOWN_MINUTES} minutos.")
    abort_shutdown()
    _write_shutdown_deadline(None)
    if minutes is None:
        return "Nenhum desligamento pendente."
    seconds = minutes * 60
    deadline = time.monotonic_ns() + minutes * NANOSECONDS_PER_MINUTE
    cmd("shutdown.exe", "/s", "/t", str(seconds))
    try:
        _write_shutdown_deadline(deadline)
    except OSError:
        abort_shutdown()
        raise
    return f"Desligamento agendado em {minutes} {'minuto' if minutes == 1 else 'minutos'}."


def repair_disk(progress=None):
    volume = os.environ.get("SystemDrive", "").strip().rstrip("\\/")
    if not re.fullmatch(r"[A-Za-z]:", volume):
        raise RuntimeError("Não foi possível identificar o volume em que o Windows está instalado.")
    return cmd("chkdsk.exe", volume, "/scan", timeout=None, success_codes=(0, 1, 2), progress=progress)


def repair_image(progress=None):
    return cmd("dism.exe", "/Online", "/Cleanup-Image", "/RestoreHealth", "/NoRestart",
               timeout=None, success_codes=(0, 3010), progress=progress)


def restore_all():
    results = []
    failures = []
    for operation in (restore_reg, lambda: services(tuple(load()["svc"]), False),
                      lambda: energy(False), lambda: hibernate(True)):
        try:
            results.append(operation())
        except (OSError, ValueError, RuntimeError) as exc:
            failures.append(str(exc))
    if failures:
        raise RuntimeError("\n".join(results + failures))
    return "\n".join(results)


def log_action(action_id, result):
    try:
        HOME.mkdir(exist_ok=True, parents=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + action_id + " " + result[-REPORT_MESSAGE_LIMIT:] + "\n")
    except OSError:
        pass


def execute(action_id, *, progress=None, shutdown_minutes=None):
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
        "repair_dism":lambda:repair_image(progress),
        "repair_sfc":lambda:cmd("sfc.exe","/scannow",timeout=None,progress=progress),
        "repair_disk":lambda:repair_disk(progress),
        "classic_on":lambda:setreg("CU",cl,"","",winreg.REG_SZ),
        "classic_off":lambda:restore_reg("CU|"+cl),
        "shutdown_15":lambda:shutdown(15),"shutdown_30":lambda:shutdown(30),
        "shutdown_60":lambda:shutdown(60),"shutdown_cancel":lambda:shutdown(None),
        "shutdown_custom":lambda:shutdown(shutdown_minutes),
        "winutil_open":open_winutil,
        "restore_point":lambda:ps("Checkpoint-Computer -Description 'Callas Optimizer' "
                                  "-RestorePointType MODIFY_SETTINGS -WarningAction Stop"),
        "restore_reg":lambda:restore_reg(),
        "restore_services":lambda:services(tuple(load()["svc"]),False),
        "restore_all":restore_all,
    }
    try:
        if action_id == "shutdown_custom" and shutdown_minutes is None:
            raise ValueError("Informe o tempo do desligamento personalizado.")
        result = tasks[action_id]()
    except Exception as exc:
        log_action(action_id, f"Falha: {exc}")
        raise
    log_action(action_id, result)
    return result


def _write_report(path, payload):
    temporary = NamedTemporaryFile(mode="w", dir=path.parent, suffix=".tmp", encoding="utf-8", delete=False)
    tmp = Path(temporary.name)
    try:
        with temporary:
            json.dump(payload, temporary, ensure_ascii=False)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def worker(action_id, filename, report_home=None, shutdown_minutes=None):
    if not re.fullmatch(r"acao-[a-f0-9]{32}\.json",filename):return 2
    # O valor informado pela interface só serve para comparação. O trabalhador
    # escreve exclusivamente na pasta do próprio perfil.
    if report_home is not None and Path(report_home) != HOME:
        return PROFILE_MISMATCH
    HOME.mkdir(exist_ok=True,parents=True)
    report = HOME / filename
    progress_report = report.with_suffix(".progress")

    def publish_progress(percent):
        try:
            _write_report(progress_report, {"percent": percent})
        except OSError:
            # A interface pode estar lendo o relatório quando ele é substituído.
            pass

    try:
        if sys.platform != "win32":
            raise OSError("Requer Windows.")
        # Trava por perfil, inclusive entre duas janelas do aplicativo.
        with (HOME / "acoes.lock").open("a+b") as lock:
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("Outra ferramenta de manutenção está em execução neste perfil.") from exc
            publish_progress(0)
            options = {"shutdown_minutes": shutdown_minutes} if action_id == "shutdown_custom" else {}
            message = execute(action_id, progress=publish_progress, **options)
            result = {"ok": True, "message": message[-REPORT_MESSAGE_LIMIT:]}
    except Exception as e:
        result = {"ok": False, "message": str(e)[-REPORT_MESSAGE_LIMIT:]}
    _write_report(report, result)
    return 0 if result["ok"] else 1
