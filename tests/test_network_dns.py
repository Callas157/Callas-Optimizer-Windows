from dataclasses import replace
from pathlib import Path
import os
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from network_dns import DnsInterface, change_dns, provider_status, read_interfaces


class NetworkDnsTest(unittest.TestCase):
    def setUp(self):
        self.adapters = {
            "ethernet": DnsInterface("ethernet", 7, "Ethernet", True, (), ("192.168.1.1",)),
            "virtual": DnsInterface("virtual", 14, "Virtual", False, ("9.9.9.9",), ("9.9.9.9",)),
        }
        self.commands = []
        self.fail_secondary = None

    def read(self):
        return list(self.adapters.values())

    def run_command(self, program, interface, family, action, option, name, *args, timeout):
        self.commands.append((program, interface, family, action, option, name, *args))
        adapter = next(item for item in self.adapters.values() if f"name={item.index}" == name)
        if action == "add" and (name, args[0]) == self.fail_secondary:
            raise RuntimeError("Falha ao adicionar DNS secundário")
        if "source=dhcp" in args:
            static, effective = (), ("192.168.1.1",)
        elif action == "set":
            static = effective = (args[1].removeprefix("address="),)
        else:
            static = effective = (*adapter.static, args[0].removeprefix("address="))
        self.adapters[adapter.guid] = replace(adapter, static=static, effective=effective)

    def change(self, action):
        return change_dns(action, self.read, self.run_command)

    def test_cloudflare_then_google_replaces_it_and_google_reverts_to_automatic(self):
        self.change("dns_cloudflare")
        self.assertEqual(provider_status(self.read()), {"dns_cloudflare": False})
        self.change("dns_google")
        self.assertEqual(self.adapters["ethernet"].static, ("8.8.8.8", "8.8.4.4"))
        self.assertEqual(provider_status(self.read()), {"dns_google": False})
        self.change("dns_google_auto")
        self.assertEqual(self.adapters["ethernet"].static, ())
        self.assertEqual(provider_status(self.read()), {})
        self.assertTrue(all("name=14" not in command for command in self.commands))
        self.assertEqual(self.adapters["virtual"].static, ("9.9.9.9",))

    def test_google_then_cloudflare_and_scoped_undo_preserves_other_dns(self):
        self.adapters["virtual"] = replace(self.adapters["virtual"], eligible=True)
        self.change("dns_google")
        self.change("dns_cloudflare")
        self.adapters["virtual"] = replace(self.adapters["virtual"],
                                           static=("9.9.9.9",), effective=("9.9.9.9",))
        self.change("dns_cloudflare_auto")
        self.assertEqual(self.adapters["ethernet"].static, ())
        self.assertEqual(self.adapters["virtual"].static, ("9.9.9.9",))

    def test_revert_removes_provider_from_a_disconnected_adapter(self):
        self.change("dns_cloudflare")
        self.adapters["ethernet"] = replace(self.adapters["ethernet"], eligible=False)
        self.assertEqual(provider_status(self.read()), {"dns_cloudflare": False})
        self.change("dns_cloudflare_auto")
        self.assertEqual(self.adapters["ethernet"].static, ())

    def test_disconnected_provider_stays_reversible_with_a_different_active_provider(self):
        self.change("dns_cloudflare")
        self.adapters["ethernet"] = replace(self.adapters["ethernet"], eligible=False)
        self.adapters["virtual"] = replace(self.adapters["virtual"], eligible=True)
        self.change("dns_google")
        self.assertEqual(provider_status(self.read()), {"dns_cloudflare": True, "dns_google": False})
        self.change("dns_cloudflare_auto")
        self.assertEqual(provider_status(self.read()), {"dns_google": False})

    def test_failed_secondary_rolls_back_previous_interfaces_and_the_partial_write(self):
        self.adapters["virtual"] = replace(self.adapters["virtual"], eligible=True)
        self.fail_secondary = ("name=14", "address=8.8.4.4")
        with self.assertRaisesRegex(RuntimeError, "secundário"):
            self.change("dns_google")
        self.assertEqual(self.adapters["ethernet"].static, ())
        self.assertEqual(self.adapters["virtual"].static, ("9.9.9.9",))
        self.assertEqual(provider_status(self.read()), {})

    def test_dhcp_provider_addresses_do_not_count_as_static_configuration(self):
        self.adapters["ethernet"] = replace(self.adapters["ethernet"], effective=("1.1.1.1", "1.0.0.1"))
        self.assertEqual(provider_status(self.read()), {})

    def test_missing_eligible_interface_explains_problem_without_mutation(self):
        del self.adapters["ethernet"]
        with self.assertRaisesRegex(RuntimeError, "rota padrão"):
            self.change("dns_google")
        self.assertEqual(self.commands, [])


    def test_inventory_excludes_active_adapter_missing_a_dns_client(self):
        powershell = os.environ.get("CALLAS_TEST_POWERSHELL") or shutil.which("powershell") or shutil.which("pwsh")
        if not powershell:
            self.skipTest("PowerShell required")
        fixture = r"""
        $ErrorActionPreference = 'Stop'
        function Get-NetAdapter {
            param([switch]$IncludeHidden)
            [pscustomobject]@{ InterfaceIndex = 7; Status = 'Up'; InterfaceGuid = '{12345678-1234-1234-1234-123456789abc}' }
            [pscustomobject]@{ InterfaceIndex = 14; Status = 'Up'; InterfaceGuid = '{23456789-1234-1234-1234-123456789abc}' }
        }
        function Get-NetIPInterface {
            param($AddressFamily)
            [pscustomobject]@{ InterfaceIndex = 7; ConnectionState = 'Connected' }
            [pscustomobject]@{ InterfaceIndex = 14; ConnectionState = 'Connected' }
        }
        function Get-NetRoute {
            param($AddressFamily, $PolicyStore)
            [pscustomobject]@{ InterfaceIndex = 7; DestinationPrefix = '0.0.0.0/0' }
            [pscustomobject]@{ InterfaceIndex = 14; DestinationPrefix = '0.0.0.0/0' }
        }
        function Get-DnsClientServerAddress {
            param($AddressFamily)
            [pscustomobject]@{ InterfaceIndex = 7; InterfaceAlias = 'Ethernet'; ServerAddresses = @('1.1.1.1','1.0.0.1') }
        }
        function Get-Item {
            param($LiteralPath, $ErrorAction)
            $item = [pscustomobject]@{}
            $item | Add-Member ScriptMethod GetValue { param($name, $default) '1.1.1.1, 1.0.0.1' } -PassThru
        }
        """

        def ps(script):
            return subprocess.run([powershell, "-NoProfile", "-NonInteractive", "-Command", fixture + script],
                                  capture_output=True, text=True, check=True, timeout=20).stdout

        interfaces = read_interfaces(ps)
        self.assertEqual([adapter.index for adapter in interfaces if adapter.eligible], [7])
        self.assertEqual(provider_status(interfaces), {"dns_cloudflare": False})

    @unittest.skipUnless(sys.platform == "win32", "Windows network inventory required")
    def test_windows_dns_inventory_and_netsh_accept_current_interface(self):
        import windows_actions

        eligible = [adapter for adapter in read_interfaces(windows_actions.ps) if adapter.eligible]
        self.assertTrue(eligible, "Sem interface IPv4 de Internet no ambiente Windows de teste")
        for adapter in eligible:
            with self.subTest(name=adapter.name, index=adapter.index):
                response = windows_actions.cmd("netsh.exe", "interface", "ipv4", "show", "dnsservers",
                                               f"name={adapter.index}")
                self.assertIn(adapter.name, response)
