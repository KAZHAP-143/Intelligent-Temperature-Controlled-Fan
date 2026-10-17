
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from fan_controller import FanController


def analyze_performance(
    heat_input=100.0,
    duration=600,
    time_step=1.0,
    target_temperature=40.0,
    settling_tolerance=0.1,
):
    params = ThermalParameters()
    controller = FanController()

    temperature = params.ambient_temperature
    history = []

    steps = int(duration / time_step)

    for step in range(steps + 1):
        time = step * time_step
        fan_speed = controller.calculate_speed(temperature)

        history.append((time, temperature, fan_speed))

        if step == steps:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat_input,
            fan_speed=fan_speed,
            params=params,
        )

        temperature += rate * time_step

    peak_temperature = max(point[1] for point in history)
    final_temperature = history[-1][1]
    final_fan_speed = history[-1][2]

    # Settling time relative to the final simulated temperature:
    # earliest point after which all samples stay within tolerance.
    settling_time = None

    for index, (time, temp, _) in enumerate(history):
        if all(
            abs(point[1] - final_temperature) <= settling_tolerance
            for point in history[index:]
        ):
            settling_time = time
            break

    steady_state_error = final_temperature - target_temperature

    print("CONTROLLER PERFORMANCE ANALYSIS")
    print("-" * 55)
    print(f"Heat input:            {heat_input:.1f} W")
    print(f"Peak temperature:      {peak_temperature:.2f} °C")
    print(f"Final temperature:     {final_temperature:.2f} °C")
    print(f"Final fan speed:       {final_fan_speed * 100:.1f}%")
    print(f"Settling time (±0.1°C): {settling_time:.1f} s")
    print(f"Target temperature:    {target_temperature:.2f} °C")
    print(f"Final tracking error:  {steady_state_error:+.2f} °C")

    return {
        "peak_temperature": peak_temperature,
        "final_temperature": final_temperature,
        "final_fan_speed": final_fan_speed,
        "settling_time": settling_time,
        "steady_state_error": steady_state_error,
    }


if __name__ == "__main__":
    analyze_performance()
