
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from fan_controller import FanController


def simulate(heat_input=100.0, duration=600, time_step=1.0):
    """Simulate the closed-loop system and return its history."""
    params = ThermalParameters()
    controller = FanController()

    temperature = params.ambient_temperature
    history = []

    steps = int(duration / time_step)

    for step in range(steps + 1):
        fan_speed = controller.calculate_speed(temperature)
        history.append((temperature, fan_speed))

        if step == steps:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat_input,
            fan_speed=fan_speed,
            params=params,
        )
        temperature += rate * time_step

    return history


class TestClosedLoopSimulation(unittest.TestCase):

    def test_initial_temperature(self):
        history = simulate()
        self.assertEqual(history[0][0], 25.0)

    def test_temperature_increases_with_heat(self):
        history = simulate()
        self.assertGreater(history[60][0], history[0][0])

    def test_fan_speed_within_limits(self):
        history = simulate()
        for temperature, speed in history:
            self.assertGreaterEqual(speed, 0.0)
            self.assertLessEqual(speed, 1.0)

    def test_temperature_stabilizes(self):
        history = simulate()
        self.assertLess(
            abs(history[-1][0] - history[-61][0]),
            0.1
        )

    def test_final_temperature_range(self):
        history = simulate()
        final_temperature = history[-1][0]
        self.assertGreater(final_temperature, 40.0)
        self.assertLess(final_temperature, 42.0)

    def test_no_heat_remains_at_ambient(self):
        history = simulate(heat_input=0.0)
        self.assertAlmostEqual(history[-1][0], 25.0)

    def test_fan_responds_to_temperature(self):
        history = simulate()
        self.assertGreater(history[120][1], history[30][1])

    def test_equilibrium_heat_balance(self):
        history = simulate()
        final_temperature, final_speed = history[-1]

        rate = temperature_rate(
            temperature=final_temperature,
            heat_input=100.0,
            fan_speed=final_speed,
            params=ThermalParameters(),
        )

        self.assertAlmostEqual(rate, 0.0, delta=0.001)


if __name__ == "__main__":
    unittest.main()
