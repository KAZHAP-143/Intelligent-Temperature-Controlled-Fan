
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermal_safety import ThermalSafetyController


class TestThermalSafety(unittest.TestCase):

    def setUp(self):
        self.safety = ThermalSafetyController()

    def test_01_normal_temperature(self):
        result = self.safety.evaluate(40.0, 0.4)
        self.assertEqual(result.status, "NORMAL")
        self.assertEqual(result.fan_speed, 0.4)

    def test_02_below_warning_threshold(self):
        result = self.safety.evaluate(49.9, 0.5)
        self.assertEqual(result.status, "NORMAL")

    def test_03_warning_threshold(self):
        result = self.safety.evaluate(50.0, 0.4)
        self.assertEqual(result.status, "WARNING")

    def test_04_warning_preserves_requested_speed(self):
        result = self.safety.evaluate(54.0, 0.6)
        self.assertEqual(result.fan_speed, 0.6)

    def test_05_critical_threshold(self):
        result = self.safety.evaluate(55.0, 0.2)
        self.assertEqual(result.status, "CRITICAL")
        self.assertEqual(result.fan_speed, 1.0)

    def test_06_above_critical_threshold(self):
        result = self.safety.evaluate(70.0, 0.0)
        self.assertEqual(result.status, "CRITICAL")
        self.assertEqual(result.fan_speed, 1.0)

    def test_07_nan_sensor_fault(self):
        result = self.safety.evaluate(float("nan"), 0.4)
        self.assertEqual(result.status, "SENSOR_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

    def test_08_infinite_sensor_fault(self):
        result = self.safety.evaluate(float("inf"), 0.4)
        self.assertEqual(result.status, "SENSOR_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

    def test_09_invalid_sensor_type(self):
        result = self.safety.evaluate(None, 0.4)
        self.assertEqual(result.status, "SENSOR_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

    def test_10_fan_speed_upper_limit(self):
        result = self.safety.evaluate(40.0, 1.5)
        self.assertEqual(result.fan_speed, 1.0)

    def test_11_fan_speed_lower_limit(self):
        result = self.safety.evaluate(40.0, -0.5)
        self.assertEqual(result.fan_speed, 0.0)

    def test_12_invalid_threshold_configuration(self):
        with self.assertRaises(ValueError):
            ThermalSafetyController(
                warning_temperature=60.0,
                critical_temperature=55.0,
            )


    def test_13_critical_overrides_low_pi_command(self):
        result = self.safety.evaluate(
            temperature=60.0,
            requested_fan_speed=0.2,
        )

        self.assertEqual(result.status, "CRITICAL")
        self.assertEqual(result.fan_speed, 1.0) 
    
    def test_14_nan_fan_command(self):
        result = self.safety.evaluate(40.0, float("nan"))
        self.assertEqual(result.status, "ACTUATOR_COMMAND_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

    def test_15_infinite_fan_command(self):
        result = self.safety.evaluate(40.0, float("inf"))
        self.assertEqual(result.status, "ACTUATOR_COMMAND_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

    def test_16_none_fan_command(self):
        result = self.safety.evaluate(40.0, None)
        self.assertEqual(result.status, "ACTUATOR_COMMAND_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

    def test_17_string_fan_command(self):
        result = self.safety.evaluate(40.0, "invalid")
        self.assertEqual(result.status, "ACTUATOR_COMMAND_FAULT")
        self.assertEqual(result.fan_speed, 1.0)

if __name__ == "__main__":
    unittest.main()
