"""Exercita a persistência do prazo sem desligar a máquina de teste."""
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import windows_actions as actions


class ShutdownTimerTest(unittest.TestCase):
    def setUp(self):
        self.deadline = None
        self.enterContext(patch.object(actions, "_read_shutdown_deadline", side_effect=lambda: self.deadline))
        self.enterContext(patch.object(actions, "_write_shutdown_deadline", side_effect=self.write_deadline))
        self.command = self.enterContext(patch.object(actions, "cmd", return_value="OK"))
        self.uptime = self.enterContext(patch.object(actions.time, "monotonic_ns", return_value=10000_000_000_000))

    def write_deadline(self, deadline):
        self.deadline = deadline

    def test_persists_minutes_and_expires(self):
        actions.shutdown(35)
        self.command.assert_has_calls([call("shutdown.exe", "/a", success_codes=(0, 1116)),
                                       call("shutdown.exe", "/s", "/t", "2100")])
        self.assertEqual(actions.remaining_shutdown_minutes(), 35)
        self.uptime.return_value += (30 * 60 + 15) * 1_000_000_000
        self.assertEqual(actions.remaining_shutdown_minutes(), 5)
        self.uptime.return_value += 5 * 60 * 1_000_000_000
        self.assertIsNone(actions.remaining_shutdown_minutes())

    def test_cancel_and_replace_share_the_saved_deadline(self):
        actions.shutdown(34)
        actions.shutdown(15)
        self.assertEqual(actions.remaining_shutdown_minutes(), 15)
        actions.shutdown(None)
        self.assertIsNone(actions.remaining_shutdown_minutes())

    def test_failed_replacement_clears_previous_deadline(self):
        actions.shutdown(34)
        self.command.side_effect = ["OK", RuntimeError("Falhou")]
        with self.assertRaises(RuntimeError):
            actions.shutdown(15)
        self.assertIsNone(actions.remaining_shutdown_minutes())

    def test_invalid_duration_does_not_touch_windows_or_existing_schedule(self):
        actions.shutdown(34)
        self.command.reset_mock()
        for minutes in (0, -1, True, 2.5, 5_256_001):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                actions.shutdown(minutes)
        self.command.assert_not_called()
        self.assertEqual(actions.remaining_shutdown_minutes(), 34)

    def test_adjusting_system_clock_does_not_change_the_countdown(self):
        with patch.object(actions.time, "time", return_value=20000) as clock:
            actions.shutdown(60)
            clock.return_value += 3600
            self.uptime.return_value += 60 * 1_000_000_000
            self.assertEqual(actions.remaining_shutdown_minutes(), 59)

    def test_write_failure_aborts_new_untracked_shutdown(self):
        with patch.object(actions, "_write_shutdown_deadline", side_effect=[None, OSError("Sem espaço")]):
            with self.assertRaisesRegex(OSError, "Sem espaço"):
                actions.shutdown(34)
        self.command.assert_has_calls([call("shutdown.exe", "/s", "/t", "2040"),
                                       call("shutdown.exe", "/a", success_codes=(0, 1116))])
