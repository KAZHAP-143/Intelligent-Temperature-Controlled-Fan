
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate


class TestThermalModel(unittest.TestCase):

    def setUp(self):
        self.params = ThermalParameters()

    def test_temperature_rate(self):
        rate = temperature_rate(
            40.0, 100.0, 0.5, self.params
        )
        self.assertAlmostEqual(rate, 0.02)

    def test_fan_increases_cooling(self):
        fan_off = temperature_rate(
            40.0, 100.0, 0.0, self.params
        )
        fan_on = temperature_rate(
            40.0, 100.0, 1.0, self.params
        )
        self.assertLess(fan_on, fan_off)

    def test_no_heat_at_ambient(self):
        rate = temperature_rate(
            25.0, 0.0, 0.0, self.params
        )
        self.assertAlmostEqual(rate, 0.0)

    def test_invalid_fan_speed(self):
        with self.assertRaises(ValueError):
            temperature_rate(
                40.0, 100.0, 1.5, self.params
            )

    def test_invalid_thermal_capacity(self):
        params = ThermalParameters(
            thermal_capacity=0.0
        )
        with self.assertRaises(ValueError):
            temperature_rate(
                40.0, 100.0, 0.5, params
            )


if __name__ == "__main__":
    unittest.main()
