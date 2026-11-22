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

    @patch.object(v, "get_vboxmanage", return_value=Path("VBoxManage.exe"))
    @patch.object(v, "_verify_guest_profile")
    @patch.object(v, "_registered_names", return_value=set(v.VM_NAMES))
    @patch.object(v.shutil, "disk_usage")
    @patch.object(v, "_run")
    def test_idempotent_does_not_touch_existing(self, commands, usage, names, profile, finder):
        usage.return_value.free = 100 * 1024**3
        with TemporaryDirectory() as folder:
            result = v.create_test_vms(Path(folder), lambda msg: None)
        self.assertIn("VMs novas: 0", result)
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
        calls = [tuple(x.args[0][1:]) for x in command.call_args_list]
        self.assertEqual(sum(x[0] == "createvm" for x in calls), 2)
        self.assertEqual(sum(x[0] == "createmedium" for x in calls), 2)
        self.assertEqual(sum(x[0] == "modifynvram" and x[2] == "secureboot" for x in calls), 2)
        self.assertNotIn("unregistervm", [x[0] for x in calls])
        self.assertTrue(any("emptydrive" in c for c in calls))
        self.assertFalse(any(str(word).lower().endswith(".iso") for c in calls for word in c))
        for call in calls:
            self.assertNotIn("delete", call)

    def test_requires_plenty_of_free_disk_before_creating(self):
        with TemporaryDirectory() as folder, \
             patch.object(v, "get_vboxmanage", return_value=Path("VBoxManage.exe")), \
             patch.object(v.shutil, "disk_usage") as usage, \
             patch.object(v, "_run") as cmd:
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
