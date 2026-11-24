"""DNS IPv4 das interfaces de Internet com confirmação e reversão de falhas."""
from dataclasses import dataclass
from ipaddress import IPv4Address
import json
from subprocess import SubprocessError
import time


DNS_PROVIDERS = {
    "dns_cloudflare": ("1.1.1.1", "1.0.0.1"),
    "dns_google": ("8.8.8.8", "8.8.4.4"),
}
DNS_REVERSALS = {
    "dns_cloudflare_auto": "dns_cloudflare",
    "dns_google_auto": "dns_google",
}

DNS_INVENTORY = r"""
    $adapters = @{}
    foreach ($adapter in Get-NetAdapter -IncludeHidden) {
        $adapters[[int]$adapter.InterfaceIndex] = $adapter
    }
    $connected = @{}
    foreach ($ip in Get-NetIPInterface -AddressFamily IPv4) {
        if ($ip.ConnectionState -eq 'Connected') { $connected[[int]$ip.InterfaceIndex] = $true }
    }
    $routes = @{}
    foreach ($route in Get-NetRoute -AddressFamily IPv4 -PolicyStore ActiveStore) {
        if ($route.DestinationPrefix -eq '0.0.0.0/0') { $routes[[int]$route.InterfaceIndex] = $true }
    }
    $interfaces = @(foreach ($client in Get-DnsClientServerAddress -AddressFamily IPv4) {
        $index = [int]$client.InterfaceIndex
        $adapter = $adapters[$index]
        if (!$adapter -or !$adapter.InterfaceGuid -or $index -le 1) { continue }
        $guid = ([guid]$adapter.InterfaceGuid).ToString('B')
        $path = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\' + $guid
        $settings = Get-Item -LiteralPath $path -ErrorAction SilentlyContinue
        if (!$settings) { continue }
        $static = @((($settings.GetValue('NameServer', '') -join ',') -split '[,;\s]+') |
                    Where-Object { $_ })
        [pscustomobject]@{
            guid = $guid
            index = $index
            name = [string]$client.InterfaceAlias
            eligible = $connected.ContainsKey($index) -and $routes.ContainsKey($index)
            static = $static
            effective = @($client.ServerAddresses | Where-Object { $_ })
        }
    })
    ConvertTo-Json -InputObject $interfaces -Depth 3 -Compress
"""


@dataclass(frozen=True)
class DnsInterface:
    guid: str
    index: int
    name: str
    eligible: bool
    static: tuple[str, ...]
    effective: tuple[str, ...]


def read_interfaces(ps) -> list[DnsInterface]:
    try:
        rows = json.loads(ps(DNS_INVENTORY))
    except ValueError as exc:
        raise RuntimeError("O Windows não retornou um inventário de DNS válido.") from exc
    if not isinstance(rows, list):
        raise RuntimeError("O Windows não retornou uma lista de interfaces de DNS.")
    interfaces = []
    for row in rows:
        try:
            static = tuple(str(IPv4Address(address)) for address in row["static"])
            interface = DnsInterface(row["guid"], row["index"], row["name"], row["eligible"],
                                     static, tuple(row["effective"]))
        except (KeyError, TypeError, ValueError):
            # Avoid changing an interface whose original static values cannot be restored.
            continue
        interfaces.append(interface)
    return interfaces


def _uses_provider(adapter: DnsInterface, addresses: tuple[str, ...]) -> bool:
    return bool(adapter.static) and set(adapter.static).issubset(addresses)


def provider_status(interfaces: list[DnsInterface]) -> dict[str, bool]:
    """Map each configured provider to whether it can be applied on more active interfaces."""
    return {
        provider: any(adapter.eligible and adapter.static != addresses for adapter in interfaces)
        for provider, addresses in DNS_PROVIDERS.items()
        if any(_uses_provider(adapter, addresses) for adapter in interfaces)
    }


def _configure(cmd, index: int, addresses: tuple[str, ...]):
    prefix = ("netsh.exe", "interface", "ipv4")
    name = f"name={index}"
    if not addresses:
        cmd(*prefix, "set", "dnsservers", name, "source=dhcp", timeout=20)
        return
    cmd(*prefix, "set", "dnsservers", name, "source=static", f"address={addresses[0]}", "validate=no", timeout=20)
    for position, address in enumerate(addresses[1:], start=2):
        cmd(*prefix, "add", "dnsservers", name, f"address={address}", f"index={position}", "validate=no", timeout=20)


def _matches(adapter: DnsInterface | None, addresses: tuple[str, ...]) -> bool:
    return adapter is not None and adapter.static == addresses and (not addresses or adapter.effective == addresses)


def change_dns(action: str, read, cmd) -> str:
    if action not in DNS_PROVIDERS and action not in DNS_REVERSALS and action != "dns_auto":
        raise ValueError("Ação de DNS desconhecida.")
    previous_provider = DNS_REVERSALS.get(action)
    addresses = DNS_PROVIDERS.get(action, ())
    interfaces = read()
    if previous_provider is None:
        targets = [adapter for adapter in interfaces if adapter.eligible]
        if not targets:
            raise RuntimeError("Nenhuma interface IPv4 com rota padrão e suporte a DNS foi encontrada. "
                               "Conecte-se à rede e tente novamente.")
    else:
        targets = [adapter for adapter in interfaces if _uses_provider(adapter, DNS_PROVIDERS[previous_provider])]
    changed = []
    try:
        for adapter in targets:
            if not _matches(adapter, addresses):
                changed.append(adapter)
                _configure(cmd, adapter.index, addresses)
        if changed:
            for attempt in range(3):
                current = {adapter.guid: adapter for adapter in read()}
                pending = [adapter.name for adapter in targets if not _matches(current.get(adapter.guid), addresses)]
                if not pending:
                    break
                if attempt < 2:
                    time.sleep(0.25)
            if pending:
                raise RuntimeError("O Windows não confirmou o DNS em " + ", ".join(pending) + ".")
    except (OSError, RuntimeError, SubprocessError) as exc:
        if not changed:
            raise
        try:
            current = {adapter.guid: adapter for adapter in read()}
        except (OSError, RuntimeError, SubprocessError) as rollback_error:
            raise RuntimeError(f"{exc}\nNão foi possível verificar as interfaces para restaurar o DNS. "
                               f"{rollback_error}") from exc
        failures = []
        for adapter in reversed(changed):
            latest = current.get(adapter.guid)
            try:
                if latest is None:
                    raise RuntimeError("Interface indisponível.")
                if latest.static != adapter.static:
                    _configure(cmd, latest.index, adapter.static)
            except (OSError, RuntimeError, SubprocessError) as rollback_error:
                failures.append(f"{adapter.name}: {rollback_error}")
        if not failures:
            try:
                restored = {adapter.guid: adapter.static for adapter in read()}
                failures = [adapter.name for adapter in changed if restored.get(adapter.guid) != adapter.static]
            except (OSError, RuntimeError, SubprocessError) as rollback_error:
                failures.append(str(rollback_error))
        if failures:
            raise RuntimeError(f"{exc}\nRestauração incompleta: {'; '.join(failures)}") from exc
        raise RuntimeError(f"{exc}\nA configuração anterior foi reaplicada.") from exc
    if not targets:
        return "Nenhuma interface usa esse provedor como DNS manual."
    mode = "DNS automático" if not addresses else "DNS " + " e ".join(addresses)
    return f"{mode} confirmado em " + ", ".join(adapter.name for adapter in targets) + "."
