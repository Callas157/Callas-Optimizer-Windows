"""Prepara duas VMs de teste no VirtualBox, somente após autorização explícita.

Não baixa ISOs nem instala sistemas operacionais. Ajusta apenas CPU e
compartilhamento das VMs existentes completamente desligadas.
O VBoxManage é sempre chamado por caminho absoluto e sem shell/console visível.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
from collections.abc import Callable
from uuid import uuid4

from extra_installers import installed_program

VM_NAMES = (
    "Callas - Windows 11 Pro",
    "Callas - Windows 11 IoT Enterprise LTSC",
)
RAM_MB = 6144
CPUS = 5
VRAM_MB = 128
DISK_MB = 80 * 1024
MIN_FREE_GB = 40
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
# Somente textos do host para a VM. Proibido compartilhamento de arquivos.
VM_ACCESS_FLAGS = (
    "--clipboard-mode=hosttoguest",
    "--clipboard-file-transfers=disabled",
    "--drag-and-drop=disabled",
)


def _vm_state(vboxmanage: Path, name: str) -> str:
    info = _run(vboxmanage, "showvminfo", name, "--machinereadable")
    match = re.search(r'(?m)^VMState="([^"]+)"\s*$', info)
    if not match:
        raise RuntimeError(f"Estado da VM {name} não pôde ser confirmado.")
    return match.group(1)


def _update_existing_vm(vboxmanage: Path, name: str) -> None:
    """Preserva discos, memória, rede e sistema convidado."""
    _run(vboxmanage, "modifyvm", name, "--cpus", str(CPUS), *VM_ACCESS_FLAGS)


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


def _rollback_new_vm(vboxmanage: Path, vm_id: str, disk: Path, disk_output: str) -> str:
    # Só chamado para máquina que acabamos de criar nesta execução.
    try:
        _run(vboxmanage, "unregistervm", vm_id, "--delete")
        # O unregistervm remove apenas discos anexados à VM.
        if disk.exists():
            match = re.search(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", disk_output)
            if not match:
                raise RuntimeError(f"O UUID do disco não foi confirmado: {disk}")
            _run(vboxmanage, "closemedium", "disk", match.group(), "--delete")
            disk.parent.rmdir()
        return "A VM incompleta criada nesta operação foi revertida."
    except Exception as exc:
        return "Não foi possível reverter a VM incompleta: " + str(exc)


def create_test_vms(
    base_folder: Path,
    notify: Callable[[str], None],
    *,
    report_progress: Callable[[int], None] | None = None,
) -> str:
    """Prepara VMs e relata etapas concluídas até 99%, reservando 100% para o chamador."""
    if report_progress is not None:
        report_progress(0)
    vbox = get_vboxmanage()
    base = Path(base_folder).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError("Escolha uma pasta de destino válida.")
    _verify_guest_profile(vbox)
    existing = _registered_names(vbox)
    if any(name not in existing for name in VM_NAMES):
        if shutil.disk_usage(base).free < MIN_FREE_GB * 1024**3:
            raise RuntimeError(
                "O local escolhido tem menos de 40 GB livres. "
                "Selecione um disco com espaço para duas instalações de Windows 11."
            )

    # Validação inicial, tratamento de cada VM existente, 10 comandos e registro de cada nova.
    total_steps = 1 + sum(1 if name in existing else 11 for name in VM_NAMES)
    completed_steps = 0

    def step_completed() -> None:
        nonlocal completed_steps
        completed_steps += 1
        if report_progress is not None:
            report_progress(min(99, completed_steps * 100 // total_steps))

    def run_step(*args: str) -> None:
        _run(vbox, *args)
        step_completed()

    step_completed()
    created: list[str] = []
    updated: list[str] = []
    not_off: list[str] = []
    for name in VM_NAMES:
        if name in existing:
            state = _vm_state(vbox, name)
            if state != "poweroff":
                not_off.append(name)
                notify(f"VM {name} está {state}; desligue completamente e tente novamente.")
            else:
                _update_existing_vm(vbox, name)
                updated.append(name)
                notify(f"Configurações atualizadas: {name}. Discos e dados preservados.")
            step_completed()
            continue
        vm_dir = base / name
        if vm_dir.exists():
            raise RuntimeError(
                f"Já existe a pasta '{vm_dir}'. O Callas não sobrescreve arquivos de VMs."
            )
        notify(f"Criando {name} (6 GB RAM, 5 vCPUs, VDI dinâmico de 80 GB)…")
        vm_id = str(uuid4())
        disk = vm_dir / f"{name}.vdi"
        disk_output = ""
        registered = False
        try:
            _run(vbox, "createvm", "--name", name, "--uuid", vm_id,
                 "--ostype", "Windows11_64",
                 "--basefolder", str(base), "--register")
            registered = True
            step_completed()
            run_step("modifyvm", vm_id,
                     "--memory", str(RAM_MB), "--cpus", str(CPUS),
                     "--vram", str(VRAM_MB), "--firmware", "efi",
                     "--tpm-type", "2.0", "--graphicscontroller", "vboxsvga",
                     "--ioapic", "on", "--nic1", "nat",
                     "--boot1", "dvd", "--boot2", "disk", *VM_ACCESS_FLAGS)
            # UEFI Secure Boot configurado apenas na nova VM; nunca reinicializa NVRAM existente.
            run_step("modifynvram", vm_id, "inituefivarstore")
            run_step("modifynvram", vm_id, "enrollmssignatures")
            run_step("modifynvram", vm_id, "enrollorclpk")
            run_step("modifynvram", vm_id, "secureboot", "--enable")
            controller = "SATA Controller"
            run_step("storagectl", vm_id, "--name", controller,
                     "--add", "sata", "--controller", "IntelAhci", "--portcount", "2")
            disk_output = _run(
                vbox, "createmedium", "disk", "--filename", str(disk),
                "--size", str(DISK_MB), "--format", "VDI", "--variant", "Standard", timeout=300,
            )
            step_completed()
            run_step("storageattach", vm_id, "--storagectl", controller,
                     "--port", "0", "--device", "0", "--type", "hdd", "--medium", str(disk))
            run_step("storageattach", vm_id, "--storagectl", controller,
                     "--port", "1", "--device", "0", "--type", "dvddrive", "--medium", "emptydrive")
            # Confere se a VM ficou registrada (não basta um comando ter retornado 0).
            if name not in _registered_names(vbox):
                raise RuntimeError("O VirtualBox não registrou a máquina virtual.")
            created.append(name)
            notify(f"Preparada: {name}. Falta anexar a ISO do Windows.")
            step_completed()
        except Exception as exc:
            suffix = _rollback_new_vm(vbox, vm_id, disk, disk_output) if registered else (
                "Nenhuma VM existente foi alterada."
            )
            raise RuntimeError(f"Falha ao preparar {name}: {exc}\n{suffix}") from exc

    msg = (f"Novas: {len(created)}. Existentes atualizadas: {len(updated)}. "
           f"Não alteradas (ligadas/suspensas): {len(not_off)}.\n"
           "5 vCPUs por máquina, 6 GB RAM, disco dinâmico até 80 GB. "
           "Área de transferência: somente PC → VM. "
           "Arrastar arquivos e transferência de arquivos por clipboard: desativados.\n"
           "Copiar e colar links exige Guest Additions instalado no Windows virtual. "
           "Não altera pastas compartilhadas configuradas anteriormente.")
    notify(msg)
    return msg
