
import sys
from pathlib import Path

# Import our existing engineering models
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from fan_controller import FanController


def run_simulation():
    parameters = ThermalParameters()
    controller = FanController()

    temperature = 25.0
    heat_input = 100.0  # Watts
    time_step = 1.0      # Seconds
    duration = 600       # Seconds

    print("CLOSED-LOOP THERMAL SIMULATION")
    print("-" * 55)

    for time in range(duration + 1):

        fan_speed = controller.calculate_speed(temperature)

        if time % 30 == 0:
            print(
                f"Time: {time:3d}s | "
                f"Temperature: {temperature:6.2f}°C | "
                f"Fan Speed: {fan_speed * 100:5.1f}%"
            )

        if time == duration:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat_input,
            fan_speed=fan_speed,
            params=parameters,
        )

        # Euler numerical integration
        temperature += rate * time_step

    print("-" * 55)
    print(f"Final temperature: {temperature:.2f}°C")
    print(f"Final fan speed: {fan_speed * 100:.1f}%")


if __name__ == "__main__":
    run_simulation()
