
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyResult:
    status: str
    fan_speed: float
    message: str


class ThermalSafetyController:
    def __init__(
        self,
        warning_temperature=50.0,
        critical_temperature=55.0,
    ):
        if warning_temperature >= critical_temperature:
            raise ValueError(
                "Warning temperature must be below critical temperature"
            )

        self.warning_temperature = warning_temperature
        self.critical_temperature = critical_temperature

    def evaluate(self, temperature, requested_fan_speed):
        # Detect invalid sensor readings.
        if (
            not isinstance(temperature, (int, float))
            or not math.isfinite(temperature)
        ):
            return SafetyResult(
                status="SENSOR_FAULT",
                fan_speed=1.0,
                message="Invalid temperature reading detected",
            )

        # Critical overheating: override the PI controller.
        if temperature >= self.critical_temperature:
            return SafetyResult(
                status="CRITICAL",
                fan_speed=1.0,
                message="Critical temperature: maximum cooling activated",
            )

        # Warning: report elevated temperature.
        if temperature >= self.warning_temperature:
            return SafetyResult(
                status="WARNING",
                fan_speed=max(0.0, min(1.0, requested_fan_speed)),
                message="Temperature warning",
            )

        # Reject invalid fan commands before actuator control.
        if (
            not isinstance(requested_fan_speed, (int, float))
            or not math.isfinite(requested_fan_speed)
        ):
            return SafetyResult(
                status="ACTUATOR_COMMAND_FAULT",
                fan_speed=1.0,
                message="Invalid fan command: fail-safe cooling requested",
            )

        return SafetyResult(
            status="NORMAL",
            fan_speed=max(0.0, min(1.0, requested_fan_speed)),
            message="Temperature within normal range",
        )


if __name__ == "__main__":
    safety = ThermalSafetyController()

    for temperature in [40, 49, 50, 54, 55, 60, float("nan")]:
        result = safety.evaluate(
            temperature=temperature,
            requested_fan_speed=0.4,
        )

        print(
            f"Temperature: {temperature} | "
            f"Status: {result.status} | "
            f"Fan: {result.fan_speed * 100:.0f}%"
        )
