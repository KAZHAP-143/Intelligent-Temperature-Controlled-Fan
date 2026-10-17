
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from fan_controller import FanController
from pi_fan_controller import PIFanController


def simulate(controller, heat_input=100.0, duration=600):
    params = ThermalParameters()
    temperature = params.ambient_temperature
    history = []

    for time in range(duration + 1):
        if isinstance(controller, PIFanController):
            speed = controller.calculate_speed(
                temperature, time_step=1.0
            )
        else:
            speed = controller.calculate_speed(temperature)

        history.append((time, temperature, speed))

        if time == duration:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat_input,
            fan_speed=speed,
            params=params,
        )

        temperature += rate

    return history


def print_results(name, history, target=40.0):
    final_temperature = history[-1][1]
    final_speed = history[-1][2]
    peak_temperature = max(point[1] for point in history)
    tracking_error = final_temperature - target

    print(f"\n{name}")
    print("-" * 45)
    print(f"Final temperature: {final_temperature:.2f} °C")
    print(f"Peak temperature:  {peak_temperature:.2f} °C")
    print(f"Final fan speed:   {final_speed * 100:.1f}%")
    print(f"Tracking error:    {tracking_error:+.2f} °C")


def main():
    original = simulate(FanController())
    pi = simulate(PIFanController())

    print("FAN CONTROLLER PERFORMANCE COMPARISON")
    print("Heat Input: 100 W | Target: 40 °C")
    print("=" * 45)

    print_results("ORIGINAL CONTROLLER", original)
    print_results("PI CONTROLLER", pi)

    print("\nTIME SERIES COMPARISON")
    print("-" * 70)

    for time in range(0, 601, 60):
        print(
            f"{time:3d}s | "
            f"Original: {original[time][1]:6.2f} °C | "
            f"PI: {pi[time][1]:6.2f} °C"
        )


if __name__ == "__main__":
    main()
