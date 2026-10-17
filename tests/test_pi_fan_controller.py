
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pi_fan_controller import PIFanController


class TestPIFanController(unittest.TestCase):

    def setUp(self):
        self.controller = PIFanController()

    def test_below_target_fan_off(self):
        speed = self.controller.calculate_speed(35.0)
        self.assertEqual(speed, 0.0)

    def test_at_target_initially_off(self):
        speed = self.controller.calculate_speed(40.0)
        self.assertEqual(speed, 0.0)

    def test_proportional_response(self):
        speed = self.controller.calculate_speed(45.0)
        self.assertAlmostEqual(speed, 0.41)

    def test_integral_accumulation(self):
        first = self.controller.calculate_speed(42.0)
        second = self.controller.calculate_speed(42.0)
        self.assertGreater(second, first)

    def test_output_upper_limit(self):
        speed = self.controller.calculate_speed(100.0)
        self.assertEqual(speed, 1.0)

    def test_output_lower_limit(self):
        speed = self.controller.calculate_speed(-20.0)
        self.assertEqual(speed, 0.0)

    def test_upper_saturation_anti_windup(self):
        self.controller.calculate_speed(100.0)
        self.assertEqual(self.controller.integral, 0.0)

    def test_lower_saturation_anti_windup(self):
        self.controller.calculate_speed(20.0)
        self.assertEqual(self.controller.integral, 0.0)

    def test_reset_integral(self):
        self.controller.calculate_speed(42.0)
        self.assertNotEqual(self.controller.integral, 0.0)

        self.controller.reset()
        self.assertEqual(self.controller.integral, 0.0)

    def test_invalid_negative_kp(self):
        with self.assertRaises(ValueError):
            PIFanController(kp=-0.1)

    def test_invalid_negative_ki(self):
        with self.assertRaises(ValueError):
            PIFanController(ki=-0.01)

    def test_invalid_time_step(self):
        with self.assertRaises(ValueError):
            self.controller.calculate_speed(42.0, time_step=0.0)


if __name__ == "__main__":
    unittest.main()
