
from dataclasses import dataclass


@dataclass
class ThermalParameters:
    ambient_temperature: float = 25.0  # °C
    thermal_capacity: float = 500.0     # J/°C
    passive_cooling: float = 2.0        # W/°C
    fan_cooling: float = 8.0            # W/°C


def temperature_rate(
    temperature: float,
    heat_input: float,
    fan_speed: float,
    params: ThermalParameters,
) -> float:
    """Calculate temperature change in °C/s."""

    if not 0.0 <= fan_speed <= 1.0:
        raise ValueError("Fan speed must be between 0 and 1.")

    if params.thermal_capacity <= 0:
        raise ValueError("Thermal capacity must be positive.")

    temperature_difference = (
        temperature - params.ambient_temperature
    )

    cooling_power = (
        params.passive_cooling
        + params.fan_cooling * fan_speed
    ) * temperature_difference

    return (
        heat_input - cooling_power
    ) / params.thermal_capacity


if __name__ == "__main__":
    parameters = ThermalParameters()

    rate = temperature_rate(
        temperature=40.0,
        heat_input=100.0,
        fan_speed=0.5,
        params=parameters,
    )

    print(f"Temperature change rate: {rate:.4f} °C/s")
