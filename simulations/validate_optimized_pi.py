
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from pi_fan_controller import PIFanController


TARGET = 40.0
DURATION = 600


def simulate(kp, ki, heat_input=100.0):
    params = ThermalParameters()
    controller = PIFanController(
        target_temperature=TARGET,
        kp=kp,
        ki=ki,
    )

    temperature = params.ambient_temperature
    history = []

    for second in range(DURATION + 1):
        speed = controller.calculate_speed(
            temperature, time_step=1.0
        )

        history.append((second, temperature, speed))

        if second == DURATION:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat_input,
            fan_speed=speed,
            params=params,
        )

        temperature += rate

    return history


def calculate_metrics(history):
    temperatures = [point[1] for point in history]

    peak = max(temperatures)
    final = temperatures[-1]

    overshoot = max(0.0, peak - TARGET)
    final_error = abs(final - TARGET)

    settling_time = None
    tolerance = 0.2

    # Work backward to find the last out-of-band sample.
    last_outside = -1

    for index, temperature in enumerate(temperatures):
        if abs(temperature - TARGET) > tolerance:
            last_outside = index

    if last_outside < len(temperatures) - 1:
        settling_time = last_outside + 1

    return {
        "peak": peak,
        "final": final,
        "overshoot": overshoot,
        "final_error": final_error,
        "settling_time": settling_time,
    }


def main():
    original = simulate(kp=0.08, ki=0.002)
    optimized = simulate(kp=0.16, ki=0.004)

    original_metrics = calculate_metrics(original)
    optimized_metrics = calculate_metrics(optimized)

    print("PI CONTROLLER OPTIMIZATION VALIDATION")
    print("=" * 65)

    print(f"{'Metric':<25} {'Original PI':>15} {'Optimized PI':>15}")
    print("-" * 65)

    for metric in ["peak", "final", "overshoot", "final_error"]:
        print(
            f"{metric:<25} "
            f"{original_metrics[metric]:>15.3f} "
            f"{optimized_metrics[metric]:>15.3f}"
        )

    print(
        f"{'settling_time':<25} "
        f"{str(original_metrics['settling_time']):>15} "
        f"{str(optimized_metrics['settling_time']):>15}"
    )

    print("\nTEMPERATURE RESPONSE")
    print("-" * 65)

    for second in range(0, DURATION + 1, 60):
        print(
            f"{second:3d}s | "
            f"Original: {original[second][1]:6.2f} °C | "
            f"Optimized: {optimized[second][1]:6.2f} °C"
        )


if __name__ == "__main__":
    main()
