
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermal_model import ThermalParameters, temperature_rate  # pyright: ignore[reportMissingImports]
from pi_fan_controller import PIFanController  # pyright: ignore[reportMissingImports]


def run_controller(kp, ki, duration=600):
    params = ThermalParameters()

    controller = PIFanController(
        target_temperature=40.0,
        kp=kp,
        ki=ki,
    )

    temperature = params.ambient_temperature

    times = []
    temperatures = []
    fan_speeds = []

    for second in range(duration + 1):
        fan_speed = controller.calculate_speed(
            temperature,
            time_step=1.0,
        )

        times.append(second)
        temperatures.append(temperature)
        fan_speeds.append(fan_speed * 100)

        if second < duration:
            temperature += temperature_rate(
                temperature=temperature,
                heat_input=100.0,
                fan_speed=fan_speed,
                params=params,
            )

    return times, temperatures, fan_speeds


def main():
    time, standard_temp, standard_fan = run_controller(
        kp=0.08,
        ki=0.002,
    )

    _, optimized_temp, optimized_fan = run_controller(
        kp=0.16,
        ki=0.004,
    )

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 8), sharex=True
    )

    ax1.plot(time, standard_temp, label="Standard PI")
    ax1.plot(time, optimized_temp, label="Optimized PI")

    ax1.axhline(
        40.0,
        linestyle="--",
        color="black",
        label="Target: 40°C",
    )

    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title("PI Controller Performance Comparison")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(time, standard_fan, label="Standard PI")
    ax2.plot(time, optimized_fan, label="Optimized PI")

    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Fan Speed (%)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()

    output = ROOT / "results" / "controller_comparison.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output, dpi=200)

    print("CONTROLLER COMPARISON")
    print("-" * 45)

    for name, temperatures in [
        ("Standard PI", standard_temp),
        ("Optimized PI", optimized_temp),
    ]:
        peak = max(temperatures)
        overshoot = max(0.0, peak - 40.0)
        final_error = abs(temperatures[-1] - 40.0)

        print(
            f"{name}: "
            f"Peak={peak:.2f}°C | "
            f"Overshoot={overshoot:.2f}°C | "
            f"Final Error={final_error:.3f}°C"
        )

    print(f"\nGraph saved to: {output}")
    plt.show()


if __name__ == "__main__":
    main()
