
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulations"))

from validate_optimized_pi import (
    simulate as simulate_constant,
    calculate_metrics,
)
from validate_pi_dynamic_heat import (
    simulate as simulate_dynamic,
    calculate_metrics as dynamic_metrics,
)


ORIGINAL_KP = 0.08
ORIGINAL_KI = 0.002

OPTIMIZED_KP = 0.16
OPTIMIZED_KI = 0.004


class TestPIOptimization(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original_constant = simulate_constant(
            ORIGINAL_KP, ORIGINAL_KI
        )
        cls.optimized_constant = simulate_constant(
            OPTIMIZED_KP, OPTIMIZED_KI
        )

        cls.original_dynamic = simulate_dynamic(
            ORIGINAL_KP, ORIGINAL_KI
        )
        cls.optimized_dynamic = simulate_dynamic(
            OPTIMIZED_KP, OPTIMIZED_KI
        )

        cls.original_metrics = calculate_metrics(
            cls.original_constant
        )
        cls.optimized_metrics = calculate_metrics(
            cls.optimized_constant
        )

        cls.original_dynamic_metrics = dynamic_metrics(
            cls.original_dynamic
        )
        cls.optimized_dynamic_metrics = dynamic_metrics(
            cls.optimized_dynamic
        )

    def test_01_optimized_reduces_overshoot(self):
        self.assertLess(
            self.optimized_metrics["overshoot"],
            self.original_metrics["overshoot"],
        )

    def test_02_optimized_reduces_settling_time(self):
        self.assertLess(
            self.optimized_metrics["settling_time"],
            self.original_metrics["settling_time"],
        )

    def test_03_optimized_tracks_target(self):
        self.assertLess(
            self.optimized_metrics["final_error"],
            0.01,
        )

    def test_04_optimized_reduces_dynamic_mean_error(self):
        self.assertLess(
            self.optimized_dynamic_metrics["mean_absolute_error"],
            self.original_dynamic_metrics["mean_absolute_error"],
        )

    def test_05_optimized_reduces_dynamic_final_error(self):
        self.assertLess(
            self.optimized_dynamic_metrics["final_error"],
            self.original_dynamic_metrics["final_error"],
        )

    def test_06_fan_speed_stays_within_limits(self):
        for point in self.optimized_dynamic:
            self.assertGreaterEqual(point["fan_speed"], 0.0)
            self.assertLessEqual(point["fan_speed"], 1.0)

    def test_07_constant_simulation_length(self):
        self.assertEqual(len(self.optimized_constant), 601)

    def test_08_dynamic_simulation_repeatability(self):
        repeated = simulate_dynamic(
            OPTIMIZED_KP, OPTIMIZED_KI
        )

        self.assertEqual(
            repeated,
            self.optimized_dynamic,
        )


if __name__ == "__main__":
    unittest.main()
