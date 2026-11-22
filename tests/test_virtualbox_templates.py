"""Testes não destrutivos do laboratório VirtualBox."""
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import virtualbox_templates as v


class VirtualBoxTemplatesTest(unittest.TestCase):
    def test_defaults_and_two_independent_guests(self):
        self.assertEqual(len(v.VM_NAMES), 2)
        self.assertIn("Windows 11 Pro", v.VM_NAMES[0])
        self.assertIn("IoT Enterprise LTSC", v.VM_NAMES[1])
        self.assertEqual(v.DISK_MB, 80 * 1024)
        self.assertEqual(v.RAM_MB, 6144)
        self.assertEqual(v.CPUS, 5)
        self.assertEqual(v.VM_ACCESS_FLAGS, (
            "--clipboard-mode=hosttoguest",
            "--clipboard-file-transfers=disabled",
            "--drag-and-drop=disabled",
        ))

    @patch.object(v, "get_vboxmanage", return_value=Path("VBoxManage.exe"))
    @patch.object(v, "_verify_guest_profile")
    @patch.object(v, "_registered_names", return_value=set(v.VM_NAMES))
    @patch.object(v, "_vm_state", return_value="poweroff")
    @patch.object(v, "_verify_guest_profile")
    @patch.object(v, "_run")
    def test_update_existing_without_touching_disks(self, commands, profile, states, names):
        with TemporaryDirectory() as folder:
            result = v.create_test_vms(Path(folder), lambda msg: None)
        self.assertIn("Existentes atualizadas: 2", result)
        self.assertEqual(commands.call_count, 2)
        for call in commands.call_args_list:
            self.assertEqual(call.args[1], "modifyvm")
            self.assertEqual(call.args[3:], ("--cpus", "5", *v.VM_ACCESS_FLAGS))
            self.assertNotIn("unregistervm", call.args)
            self.assertNotIn("createmedium", call.args)

    @patch.object(v, "_registered_names", return_value=set(v.VM_NAMES))
    @patch.object(v, "_vm_state", return_value="running")
    @patch.object(v, "_verify_guest_profile")
    @patch.object(v, "_run")
    def test_running_vm_is_never_modified(self, commands, profile, states, names):
        with TemporaryDirectory() as folder:
            result = v.create_test_vms(Path(folder), lambda msg: None)
        self.assertIn("Não alteradas (ligadas/suspensas): 2", result)
        commands.assert_not_called()

    @patch.object(v, "get_vboxmanage", return_value=Path("VBoxManage.exe"))
    @patch.object(v, "_verify_guest_profile")
    @patch.object(v, "_registered_names")
    @patch.object(v.shutil, "disk_usage")
    @patch.object(v, "_run")
    def test_creates_only_two_templates_without_isos(self, command, usage, names, profile, finder):
        usage.return_value.free = 100 * 1024**3
        # Consulta inicial, primeira VM criada, segunda VM criada.
        names.side_effect = [set(), {v.VM_NAMES[0]}, set(v.VM_NAMES)]
        with TemporaryDirectory() as folder:
            result = v.create_test_vms(Path(folder), lambda msg: None)
        self.assertIn("VMs novas: 2", result)
        calls = [tuple(x.args[1:]) for x in command.call_args_list]
        self.assertEqual(sum(x[0] == "createvm" for x in calls), 2)
        self.assertEqual(sum(x[0] == "createmedium" for x in calls), 2)
        self.assertEqual(sum(x[0] == "modifynvram" and x[2] == "secureboot" for x in calls), 2)
        vm_modifications = [x for x in calls if x[0] == "modifyvm"]
        self.assertEqual(len(vm_modifications), 2)
        for change in vm_modifications:
            self.assertEqual(change[change.index("--cpus") + 1], "5")
            for flag in v.VM_ACCESS_FLAGS:
                self.assertIn(flag, change)
        self.assertNotIn("unregistervm", [x[0] for x in calls])
        self.assertTrue(any("emptydrive" in c for c in calls))
        self.assertFalse(any(str(word).lower().endswith(".iso") for c in calls for word in c))
        for call in calls:
            self.assertNotIn("delete", call)

    def test_requires_plenty_of_free_disk_before_creating(self):
        with TemporaryDirectory() as folder, \
             patch.object(v, "get_vboxmanage", return_value=Path("VBoxManage.exe")), \
             patch.object(v.shutil, "disk_usage") as usage, \
             patch.object(v, "_run") as cmd, \
             patch.object(v, "_registered_names", return_value=set()), \
             patch.object(v, "_verify_guest_profile"):
            usage.return_value.free = 5 * 1024**3
            with self.assertRaisesRegex(RuntimeError, "menos de 40 GB"):
                v.create_test_vms(Path(folder), lambda msg: None)
            cmd.assert_not_called()

    def test_no_shell_commands_in_source(self):
        s=(ROOT/"src/virtualbox_templates.py").read_text(encoding="utf-8")
        self.assertIn("shell=False", s)
        self.assertNotIn("powershell.exe", s)
        self.assertNotIn("shell=True", s)


if __name__ == "__main__":
    unittest.main()
