
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from thermal_model import ThermalParameters, temperature_rate
from pi_fan_controller import PIFanController


TARGET = 40.0
DURATION = 600
TOLERANCE = 0.2


def simulate(kp, ki):
    params = ThermalParameters()
    controller = PIFanController(
        target_temperature=TARGET,
        kp=kp,
        ki=ki,
    )

    temperature = params.ambient_temperature
    temperatures = []

    for second in range(DURATION + 1):
        speed = controller.calculate_speed(
            temperature, time_step=1.0
        )

        temperatures.append(temperature)

        if second == DURATION:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=100.0,
            fan_speed=speed,
            params=params,
        )

        temperature += rate

    peak = max(temperatures)
    overshoot = max(0.0, peak - TARGET)
    final_error = abs(temperatures[-1] - TARGET)

    # Settling time: first sample after which the entire
    # remaining trajectory stays within ±0.2°C of target.
    settling_time = None

    for index in range(len(temperatures)):
        if all(
            abs(value - TARGET) <= TOLERANCE
            for value in temperatures[index:]
        ):
            settling_time = index
            break

    return {
        "kp": kp,
        "ki": ki,
        "peak": peak,
        "overshoot": overshoot,
        "final_error": final_error,
        "settling_time": settling_time,
    }


def optimize():
    kp_values = [0.04, 0.06, 0.08, 0.10, 0.12, 0.16]
    ki_values = [0.0002, 0.0005, 0.001, 0.002, 0.004]

    results = []

    for kp in kp_values:
        for ki in ki_values:
            result = simulate(kp, ki)

            # Penalize controllers that fail to settle.
            settling = result["settling_time"]
            settling_penalty = (
                settling if settling is not None else 1200
            )

            # Weighted engineering objective
            result["score"] = (
                10.0 * result["overshoot"]
                + 20.0 * result["final_error"]
                + 0.01 * settling_penalty
            )

            results.append(result)

    results.sort(key=lambda result: result["score"])

    print("AUTOMATED PI GAIN OPTIMIZATION")
    print("=" * 75)
    print(f"Evaluated {len(results)} gain combinations")
    print()
    print("TOP 10 CONTROLLER CONFIGURATIONS")
    print("-" * 75)

    for index, result in enumerate(results[:10], start=1):
        settling = result["settling_time"]
        settling_text = (
            f"{settling}s" if settling is not None else "Not settled"
        )

        print(
            f"{index:2d}. "
            f"Kp={result['kp']:.4f} | "
            f"Ki={result['ki']:.4f} | "
            f"Overshoot={result['overshoot']:.2f}°C | "
            f"Error={result['final_error']:.3f}°C | "
            f"Settling={settling_text} | "
            f"Score={result['score']:.3f}"
        )

    best = results[0]

    print("\nBEST CONTROLLER")
    print("-" * 75)
    print(f"Kp:            {best['kp']}")
    print(f"Ki:            {best['ki']}")
    print(f"Peak:          {best['peak']:.2f}°C")
    print(f"Overshoot:     {best['overshoot']:.2f}°C")
    print(f"Final error:   {best['final_error']:.3f}°C")
    print(f"Settling time: {best['settling_time']} seconds")

    return best


if __name__ == "__main__":
    optimize()
