
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "simulations"))

from thermal_model import ThermalParameters, temperature_rate
from pi_fan_controller import PIFanController
from dynamic_heat_simulation import get_heat_input


TARGET = 40.0
DURATION = 600


def simulate(kp, ki):
    params = ThermalParameters()
    controller = PIFanController(
        target_temperature=TARGET,
        kp=kp,
        ki=ki,
    )

    temperature = params.ambient_temperature
    history = []

    for second in range(DURATION + 1):
        heat = get_heat_input(second)
        speed = controller.calculate_speed(
            temperature, time_step=1.0
        )

        history.append({
            "time": second,
            "heat": heat,
            "temperature": temperature,
            "fan_speed": speed,
        })

        if second == DURATION:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat,
            fan_speed=speed,
            params=params,
        )

        temperature += rate

    return history


def calculate_metrics(history):
    temperatures = [point["temperature"] for point in history]
    speeds = [point["fan_speed"] for point in history]

    return {
        "peak": max(temperatures),
        "final": temperatures[-1],
        "final_error": abs(temperatures[-1] - TARGET),
        "max_fan_speed": max(speeds),
        "mean_absolute_error": sum(
            abs(temp - TARGET) for temp in temperatures
        ) / len(temperatures),
    }


def main():
    original = simulate(kp=0.08, ki=0.002)
    optimized = simulate(kp=0.16, ki=0.004)

    original_metrics = calculate_metrics(original)
    optimized_metrics = calculate_metrics(optimized)

    print("DYNAMIC HEAT LOAD — PI CONTROLLER VALIDATION")
    print("=" * 70)

    print(f"{'Metric':<25} {'Original PI':>15} {'Optimized PI':>15}")
    print("-" * 70)

    for metric in original_metrics:
        print(
            f"{metric:<25} "
            f"{original_metrics[metric]:>15.3f} "
            f"{optimized_metrics[metric]:>15.3f}"
        )

    print("\nTEMPERATURE RESPONSE")
    print("-" * 70)

    for second in range(0, DURATION + 1, 30):
        old = original[second]
        new = optimized[second]

        print(
            f"{second:3d}s | "
            f"Heat: {old['heat']:5.0f} W | "
            f"Original: {old['temperature']:6.2f}°C | "
            f"Optimized: {new['temperature']:6.2f}°C | "
            f"Fan: {new['fan_speed'] * 100:5.1f}%"
        )


if __name__ == "__main__":
    main()
