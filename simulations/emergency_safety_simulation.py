
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermal_model import ThermalParameters, temperature_rate
from pi_fan_controller import PIFanController
from thermal_safety import ThermalSafetyController


def simulate(duration=600):
    params = ThermalParameters()
    controller = PIFanController(
        target_temperature=40.0,
        kp=0.16,
        ki=0.004,
    )
    safety = ThermalSafetyController()

    temperature = params.ambient_temperature
    history = []

    for second in range(duration + 1):
        # Severe heat load from 120s to 359s.
        heat = 400.0 if 120 <= second < 360 else 100.0

        requested_speed = controller.calculate_speed(
            temperature,
            time_step=1.0,
        )

        result = safety.evaluate(
            temperature,
            requested_speed,
        )

        history.append({
            "time": second,
            "heat": heat,
            "temperature": temperature,
            "requested_speed": requested_speed,
            "fan_speed": result.fan_speed,
            "status": result.status,
        })

        if second == duration:
            break

        rate = temperature_rate(
            temperature=temperature,
            heat_input=heat,
            fan_speed=result.fan_speed,
            params=params,
        )
        temperature += rate

    return history


def main():
    history = simulate()

    print("EMERGENCY THERMAL SAFETY SIMULATION")
    print("=" * 75)

    print(
        f"{'Time':>5} | {'Heat':>6} | {'Temp':>8} | "
        f"{'PI Fan':>7} | {'Final Fan':>9} | Status"
    )
    print("-" * 75)

    for point in history:
        if point["time"] % 30 == 0:
            print(
                f"{point['time']:5d} | "
                f"{point['heat']:6.0f} | "
                f"{point['temperature']:8.2f} | "
                f"{point['requested_speed'] * 100:6.1f}% | "
                f"{point['fan_speed'] * 100:8.1f}% | "
                f"{point['status']}"
            )

    print("\nSAFETY SUMMARY")
    print("-" * 40)

    for status in ["NORMAL", "WARNING", "CRITICAL", "SENSOR_FAULT"]:
        count = sum(
            point["status"] == status for point in history
        )
        print(f"{status:<15}: {count} samples")

    peak = max(point["temperature"] for point in history)
    print(f"\nPeak temperature: {peak:.2f}°C")

    for status in ["WARNING", "CRITICAL"]:
        first = next(
            (point for point in history if point["status"] == status),
            None,
        )
        if first is not None:
            print(
                f"First {status}: {first['time']}s "
                f"at {first['temperature']:.2f}°C"
            )


if __name__ == "__main__":
    main()
