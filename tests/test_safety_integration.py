
import sys
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulations"))
sys.path.insert(0, str(ROOT / "src"))

from safe_closed_loop_simulation import simulate as simulate_safe
from emergency_safety_simulation import simulate as simulate_emergency
from sensor_fault_simulation import simulate as simulate_sensor_fault
from thermal_safety import ThermalSafetyController


class TestSafetyIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.normal = simulate_safe()
        cls.emergency = simulate_emergency()
        cls.sensor_fault = simulate_sensor_fault()

    def test_01_normal_simulation_length(self):
        self.assertEqual(len(self.normal), 601)

    def test_02_normal_simulation_stays_below_warning(self):
        self.assertTrue(
            all(point["status"] == "NORMAL" for point in self.normal)
        )

    def test_03_emergency_reaches_warning(self):
        self.assertTrue(
            any(point["status"] == "WARNING" for point in self.emergency)
        )

    def test_04_emergency_reaches_critical(self):
        self.assertTrue(
            any(point["status"] == "CRITICAL" for point in self.emergency)
        )

    def test_05_critical_always_commands_full_fan(self):
        critical = [
            point for point in self.emergency
            if point["status"] == "CRITICAL"
        ]
        self.assertGreater(len(critical), 0)
        self.assertTrue(
            all(point["fan_speed"] == 1.0 for point in critical)
        )

    def test_06_emergency_recovers(self):
        self.assertEqual(self.emergency[-1]["status"], "NORMAL")
        self.assertLess(
            abs(self.emergency[-1]["temperature"] - 40.0),
            0.2,
        )

    def test_07_sensor_fault_duration(self):
        faults = [
            point for point in self.sensor_fault
            if point["status"] == "SENSOR_FAULT"
        ]
        self.assertEqual(len(faults), 50)

    def test_08_sensor_fault_commands_full_fan(self):
        faults = [
            point for point in self.sensor_fault
            if point["status"] == "SENSOR_FAULT"
        ]
        self.assertTrue(
            all(point["fan_speed"] == 1.0 for point in faults)
        )

    def test_09_sensor_recovers_at_250s(self):
        self.assertEqual(
            self.sensor_fault[250]["status"], "NORMAL"
        )

    def test_10_actual_temperature_remains_finite(self):
        self.assertTrue(
            all(
                math.isfinite(point["actual_temperature"])
                for point in self.sensor_fault
            )
        )

    def test_11_all_fan_commands_within_limits(self):
        for history in (
            self.normal,
            self.emergency,
            self.sensor_fault,
        ):
            for point in history:
                self.assertGreaterEqual(point["fan_speed"], 0.0)
                self.assertLessEqual(point["fan_speed"], 1.0)

    def test_12_safety_overrides_low_pi_command(self):
        safety = ThermalSafetyController()
        result = safety.evaluate(
            temperature=60.0,
            requested_fan_speed=0.2,
        )
        self.assertEqual(result.status, "CRITICAL")
        self.assertEqual(result.fan_speed, 1.0)


if __name__ == "__main__":
    unittest.main()
