"""Prepara duas VMs de teste no VirtualBox, somente após autorização explícita.

Não baixa ISOs, não instala sistemas operacionais e não modifica VMs já existentes.
O VBoxManage é sempre chamado por caminho absoluto e sem shell/console visível.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
from collections.abc import Callable

from extra_installers import installed_program

VM_NAMES = (
    "Callas - Windows 11 Pro",
    "Callas - Windows 11 IoT Enterprise LTSC",
)
RAM_MB = 6144
CPUS = 2
VRAM_MB = 128
DISK_MB = 80 * 1024
MIN_FREE_GB = 40
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _run(vboxmanage: Path, *args: str, timeout: int = 150) -> str:
    result = subprocess.run(
        [str(vboxmanage), *args], text=True, capture_output=True,
        encoding="utf-8", errors="replace", check=False, timeout=timeout,
        creationflags=NO_WINDOW, shell=False,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()[-1000:]
        raise RuntimeError(f"VBoxManage falhou em {args[0]} (código {result.returncode}): {detail}")
    return result.stdout


def get_vboxmanage() -> Path:
    if os.name != "nt":
        raise RuntimeError("As máquinas virtuais só podem ser preparadas no Windows.")
    executable = installed_program("virtualbox")
    if not isinstance(executable, Path) or not executable.is_file():
        raise RuntimeError("Instale o VirtualBox primeiro pela Central de Programas.")
    command = executable.parent / "VBoxManage.exe"
    if not command.is_file():
        raise RuntimeError("VBoxManage.exe não localizado na instalação oficial do VirtualBox.")
    return command


def _registered_names(vboxmanage: Path) -> set[str]:
    output = _run(vboxmanage, "list", "vms")
    names: set[str] = set()
    for line in output.splitlines():
        match = re.fullmatch(r'"(.+)" \{[0-9a-fA-F-]{36}\}', line.strip())
        if match:
            names.add(match.group(1))
    return names


def _verify_guest_profile(vboxmanage: Path) -> None:
    found = _run(vboxmanage, "list", "ostypes")
    if not re.search(r"(?m)^\s*ID:\s*Windows11_64\s*$", found):
        raise RuntimeError("Esta versão do VirtualBox não reconhece Windows 11 x64; atualize-o.")


def _rollback_new_vm(vboxmanage: Path, name: str) -> str:
    # Só chamado para máquina que acabamos de criar nesta execução.
    try:
        _run(vboxmanage, "unregistervm", name, "--delete")
        return "A VM incompleta criada nesta operação foi revertida."
    except Exception as exc:
        return "Não foi possível reverter a VM incompleta: " + str(exc)


def create_test_vms(base_folder: Path, notify: Callable[[str], None]) -> str:
    """Cria templates vazios em pasta escolhida pelo usuário; já existentes são preservados."""
    vbox = get_vboxmanage()
    base = Path(base_folder).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError("Escolha uma pasta de destino válida.")
    if shutil.disk_usage(base).free < MIN_FREE_GB * 1024**3:
        raise RuntimeError(
            "O local escolhido tem menos de 40 GB livres. "
            "Selecione um disco com espaço para duas instalações de Windows 11."
        )
    _verify_guest_profile(vbox)
    existing = _registered_names(vbox)
    created: list[str] = []
    skipped: list[str] = []
    for name in VM_NAMES:
        if name in existing:
            skipped.append(name)
            notify(f"VM existente preservada: {name}")
            continue
        vm_dir = base / name
        if vm_dir.exists():
            raise RuntimeError(
                f"Já existe a pasta '{vm_dir}'. O Callas não sobrescreve arquivos de VMs."
            )
        notify(f"Criando {name} (6 GB RAM, 2 vCPUs, VDI dinâmico de 80 GB)…")
        registered = False
        try:
            _run(vbox, "createvm", "--name", name,
                 "--platform-architecture=x86", "--ostype", "Windows11_64",
                 "--basefolder", str(base), "--register")
            registered = True
            _run(vbox, "modifyvm", name,
                 "--memory", str(RAM_MB), "--cpus", str(CPUS),
                 "--vram", str(VRAM_MB), "--firmware", "efi",
                 "--tpm-type", "2.0", "--graphicscontroller", "vboxsvga",
                 "--ioapic", "on", "--nic1", "nat",
                 "--boot1", "dvd", "--boot2", "disk")
            # UEFI Secure Boot configurado apenas na nova VM; nunca reinicializa NVRAM existente.
            _run(vbox, "modifynvram", name, "inituefivarstore")
            _run(vbox, "modifynvram", name, "enrollmssignatures")
            _run(vbox, "modifynvram", name, "enrollorclpk")
            _run(vbox, "modifynvram", name, "secureboot", "--enable")
            controller = "SATA Controller"
            _run(vbox, "storagectl", name, "--name", controller,
                 "--add", "sata", "--controller", "IntelAhci", "--portcount", "2")
            disk = vm_dir / f"{name}.vdi"
            _run(vbox, "createmedium", "disk", "--filename", str(disk),
                 "--size", str(DISK_MB), "--format", "VDI", "--variant", "Standard", timeout=300)
            _run(vbox, "storageattach", name, "--storagectl", controller,
                 "--port", "0", "--device", "0", "--type", "hdd", "--medium", str(disk))
            _run(vbox, "storageattach", name, "--storagectl", controller,
                 "--port", "1", "--device", "0", "--type", "dvddrive", "--medium", "emptydrive")
            # Confere se a VM ficou registrada (não basta um comando ter retornado 0).
            if name not in _registered_names(vbox):
                raise RuntimeError("O VirtualBox não registrou a máquina virtual.")
            created.append(name)
            notify(f"Preparada: {name}. Falta anexar a ISO do Windows.")
        except Exception as exc:
            suffix = _rollback_new_vm(vbox, name) if registered else (
                "Nenhuma VM existente foi alterada."
            )
            raise RuntimeError(f"Falha ao preparar {name}: {exc}\n{suffix}") from exc

    if not created and not skipped:
        raise RuntimeError("Nenhuma máquina virtual foi preparada.")
    msg = (f"VMs novas: {len(created)}. VMs já existentes preservadas: {len(skipped)}.\n"
           "Ambas são templates vazios: anexe a ISO do Windows correspondente "
           "pelo VirtualBox antes de iniciar.\n"
           "Os discos VDI são dinâmicos (até 80 GB cada); não há Windows pré-instalado.")
    notify(msg)
    return msg
