
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fan_controller import FanController


class TestFanController(unittest.TestCase):

    def setUp(self):
        self.controller = FanController()

    def test_fan_off_below_threshold(self):
        self.assertEqual(self.controller.calculate_speed(25), 0.0)

    def test_fan_off_at_minimum(self):
        self.assertEqual(self.controller.calculate_speed(30), 0.0)

    def test_proportional_speed(self):
        self.assertAlmostEqual(
            self.controller.calculate_speed(40), 0.5
        )

    def test_fan_full_speed(self):
        self.assertEqual(self.controller.calculate_speed(50), 1.0)

    def test_speed_limited_above_maximum(self):
        self.assertEqual(self.controller.calculate_speed(60), 1.0)

    def test_invalid_thresholds(self):
        with self.assertRaises(ValueError):
            FanController(min_temperature=50, max_temperature=30)

    def test_equal_thresholds(self):
        with self.assertRaises(ValueError):
            FanController(min_temperature=40, max_temperature=40)


if __name__ == "__main__":
    unittest.main()
