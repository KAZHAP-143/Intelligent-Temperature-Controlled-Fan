
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "simulations"))

from thermal_model import ThermalParameters, temperature_rate
from fan_controller import FanController
from dynamic_heat_simulation import get_heat_input


def simulate_dynamic_heat():
    """Run 600 seconds of dynamic heat-load simulation."""
    params = ThermalParameters()
    controller = FanController()

    temperature = 25.0
    history = []

    for time in range(601):
        heat = get_heat_input(time)
        speed = controller.calculate_speed(temperature)

        history.append({
            "time": time,
            "heat": heat,
            "temperature": temperature,
            "fan_speed": speed,
        })

        if time == 600:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat,
            fan_speed=speed,
            params=params,
        )

        temperature += rate

    return history


class TestDynamicHeatSimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.history = simulate_dynamic_heat()

    def test_initial_heat_load(self):
        self.assertEqual(get_heat_input(0), 50.0)

    def test_heat_load_transitions(self):
        self.assertEqual(get_heat_input(119), 50.0)
        self.assertEqual(get_heat_input(120), 150.0)
        self.assertEqual(get_heat_input(299), 150.0)
        self.assertEqual(get_heat_input(300), 250.0)
        self.assertEqual(get_heat_input(449), 250.0)
        self.assertEqual(get_heat_input(450), 75.0)

    def test_fan_speed_limits(self):
        for point in self.history:
            self.assertGreaterEqual(point["fan_speed"], 0.0)
            self.assertLessEqual(point["fan_speed"], 1.0)

    def test_temperature_rises_after_load_increase(self):
        self.assertGreater(
            self.history[180]["temperature"],
            self.history[120]["temperature"]
        )

    def test_fan_increases_during_high_load(self):
        self.assertGreater(
            self.history[420]["fan_speed"],
            self.history[300]["fan_speed"]
        )

    def test_temperature_drops_after_load_reduction(self):
        self.assertLess(
            self.history[510]["temperature"],
            self.history[450]["temperature"]
        )

    def test_fan_slows_after_load_reduction(self):
        self.assertLess(
            self.history[600]["fan_speed"],
            self.history[450]["fan_speed"]
        )

    def test_high_load_temperature_range(self):
        temperature = self.history[450]["temperature"]
        self.assertGreater(temperature, 49.0)
        self.assertLess(temperature, 51.0)

    def test_final_temperature_range(self):
        temperature = self.history[600]["temperature"]
        self.assertGreater(temperature, 38.0)
        self.assertLess(temperature, 40.0)

    def test_all_temperatures_finite(self):
        import math

        for point in self.history:
            self.assertTrue(math.isfinite(point["temperature"]))


if __name__ == "__main__":
    unittest.main()
