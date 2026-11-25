from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class GpuUsageTest(unittest.TestCase):
    def test_sums_processes_on_one_engine_and_uses_the_busiest_engine(self):
        from gpu_usage import busiest_engine_percent

        samples = [
            ("pid_10_luid_0x0_0x1234_phys_0_eng_0_engtype_3D", 30.0),
            ("pid_20_luid_0x0_0x1234_phys_0_eng_0_engtype_3D", 45.0),
            ("pid_20_luid_0x0_0x1234_phys_0_eng_1_engtype_Copy", 60.0),
            ("pid_20_luid_0x0_0x5678_phys_0_eng_0_engtype_3D", 50.0),
        ]
        self.assertEqual(busiest_engine_percent(samples), 75)

    def test_distinguishes_idle_from_missing_samples(self):
        from gpu_usage import busiest_engine_percent

        name = "pid_10_luid_0x0_0x1234_phys_0_eng_0_engtype_3D"
        self.assertEqual(busiest_engine_percent([(name, 0.0)]), 0)
        self.assertIsNone(busiest_engine_percent([("_Total", 52.0), (name, float("nan")), (name, -1.0)]))
        self.assertEqual(busiest_engine_percent([(name, 105.0)]), 100)
