
import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermal_model import ThermalParameters, temperature_rate
from pi_fan_controller import PIFanController
from thermal_safety import ThermalSafetyController


def heat_schedule(second):
    if second < 120:
        return 100.0
    if second < 300:
        return 250.0
    return 75.0


def simulate(duration=600):
    params = ThermalParameters()

    controller = PIFanController(
        target_temperature=40.0,
        kp=0.16,
        ki=0.004,
    )

    safety = ThermalSafetyController(
        warning_temperature=50.0,
        critical_temperature=55.0,
    )

    temperature = params.ambient_temperature
    history = []

    for second in range(duration + 1):
        heat = heat_schedule(second)

        # The thermal model provides the simulated sensor reading.
        sensor_temperature = temperature

        # Do not pass invalid sensor readings to the PI controller.
        if (
            isinstance(sensor_temperature, (int, float))
            and math.isfinite(sensor_temperature)
        ):
            requested_speed = controller.calculate_speed(
                sensor_temperature,
                time_step=1.0,
            )
        else:
            requested_speed = 1.0

        # Safety controller determines the final fan command.
        result = safety.evaluate(
            temperature=sensor_temperature,
            requested_fan_speed=requested_speed,
        )

        history.append({
            "time": second,
            "temperature": temperature,
            "heat": heat,
            "requested_speed": requested_speed,
            "fan_speed": result.fan_speed,
            "status": result.status,
        })

        if second == duration:
            break

        # The physical model uses the safety-approved command.
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

    print("SAFE CLOSED-LOOP FAN SIMULATION")
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
            point["status"] == status
            for point in history
        )
        print(f"{status:<15}: {count} samples")

    print(
        f"\nPeak temperature: "
        f"{max(p['temperature'] for p in history):.2f}°C"
    )


if __name__ == "__main__":
    main()
