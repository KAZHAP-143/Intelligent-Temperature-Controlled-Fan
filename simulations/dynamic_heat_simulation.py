
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from fan_controller import FanController


def get_heat_input(time):
    """Return heat input in watts for the current time."""
    if time < 120:
        return 50.0
    elif time < 300:
        return 150.0
    elif time < 450:
        return 250.0
    else:
        return 75.0


def run_simulation():
    params = ThermalParameters()
    controller = FanController()

    temperature = 25.0
    time_step = 1.0
    duration = 600

    print("DYNAMIC HEAT LOAD SIMULATION")
    print("-" * 75)

    for time in range(duration + 1):
        heat_input = get_heat_input(time)
        fan_speed = controller.calculate_speed(temperature)

        if time % 30 == 0:
            print(
                f"Time: {time:3d}s | "
                f"Heat: {heat_input:5.0f} W | "
                f"Temperature: {temperature:6.2f}°C | "
                f"Fan Speed: {fan_speed * 100:5.1f}%"
            )

        if time == duration:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat_input,
            fan_speed=fan_speed,
            params=params,
        )

        temperature += rate * time_step

    print("-" * 75)
    print(f"Final temperature: {temperature:.2f}°C")
    print(f"Final fan speed: {fan_speed * 100:.1f}%")


if __name__ == "__main__":
    run_simulation()
