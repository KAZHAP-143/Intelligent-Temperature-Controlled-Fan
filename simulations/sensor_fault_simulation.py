
import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thermal_model import ThermalParameters, temperature_rate
from pi_fan_controller import PIFanController
from thermal_safety import ThermalSafetyController


def simulate(duration=400):
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
        heat = 100.0

        # Inject sensor failure from 200s through 249s.
        sensor_temperature = (
            float("nan")
            if 200 <= second < 250
            else temperature
        )

        # Never pass invalid sensor readings to PI control.
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

        result = safety.evaluate(
            temperature=sensor_temperature,
            requested_fan_speed=requested_speed,
        )

        history.append({
            "time": second,
            "actual_temperature": temperature,
            "sensor_temperature": sensor_temperature,
            "requested_speed": requested_speed,
            "fan_speed": result.fan_speed,
            "status": result.status,
        })

        if second == duration:
            break

        # Use the actual simulated temperature for physics.
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

    print("TEMPERATURE SENSOR FAULT SIMULATION")
    print("=" * 75)

    for point in history:
        second = point["time"]

        if second % 25 == 0:
            sensor = point["sensor_temperature"]
            sensor_text = (
                "NaN" if not math.isfinite(sensor)
                else f"{sensor:.2f}"
            )

            print(
                f"{second:3d}s | "
                f"Actual: {point['actual_temperature']:6.2f}°C | "
                f"Sensor: {sensor_text:>6} | "
                f"Fan: {point['fan_speed'] * 100:5.1f}% | "
                f"{point['status']}"
            )

    fault_samples = [
        point for point in history
        if point["status"] == "SENSOR_FAULT"
    ]

    print("\nFAULT SUMMARY")
    print("-" * 45)
    print(f"Sensor fault samples: {len(fault_samples)}")

    all_safe = all(
        point["fan_speed"] == 1.0
        for point in fault_samples
    )

    print(f"All fault samples request 100% fan: {all_safe}")

    recovered = history[250]["status"] != "SENSOR_FAULT"
    print(f"Sensor status recovered at 250s: {recovered}")


if __name__ == "__main__":
    main()
