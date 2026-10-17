
import sys
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulations"))
sys.path.insert(0, str(ROOT / "src"))

from controller_performance import analyze_performance


class TestControllerPerformance(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Suppress printed analysis during tests
        with redirect_stdout(StringIO()):
            cls.results = analyze_performance()

    def test_peak_temperature(self):
        self.assertGreater(self.results["peak_temperature"], 40.0)
        self.assertLess(self.results["peak_temperature"], 42.0)

    def test_final_temperature(self):
        self.assertAlmostEqual(
            self.results["final_temperature"], 40.81, delta=0.1
        )

    def test_fan_speed_limits(self):
        speed = self.results["final_fan_speed"]
        self.assertGreaterEqual(speed, 0.0)
        self.assertLessEqual(speed, 1.0)

    def test_settling_time(self):
        settling = self.results["settling_time"]
        self.assertIsNotNone(settling)
        self.assertGreater(settling, 200)
        self.assertLess(settling, 250)

    def test_tracking_error(self):
        self.assertAlmostEqual(
            self.results["steady_state_error"], 0.81, delta=0.1
        )

    def test_no_temperature_overshoot(self):
        self.assertAlmostEqual(
            self.results["peak_temperature"],
            self.results["final_temperature"],
            delta=0.01
        )

    def test_higher_heat_increases_temperature(self):
        with redirect_stdout(StringIO()):
            high_load = analyze_performance(heat_input=150.0)

        self.assertGreater(
            high_load["final_temperature"],
            self.results["final_temperature"]
        )

    def test_zero_heat_remains_at_ambient(self):
        with redirect_stdout(StringIO()):
            no_load = analyze_performance(heat_input=0.0)

        self.assertAlmostEqual(
            no_load["final_temperature"], 25.0, delta=0.01
        )


if __name__ == "__main__":
    unittest.main()
