
class FanController:
    """Temperature-based proportional fan speed controller."""

    def __init__(
        self,
        min_temperature=30.0,
        max_temperature=50.0,
    ):
        if max_temperature <= min_temperature:
            raise ValueError(
                "Maximum temperature must exceed minimum temperature."
            )

        self.min_temperature = min_temperature
        self.max_temperature = max_temperature

    def calculate_speed(self, temperature):
        """Return normalized fan speed between 0.0 and 1.0."""

        if temperature <= self.min_temperature:
            return 0.0

        if temperature >= self.max_temperature:
            return 1.0

        speed = (
            (temperature - self.min_temperature)
            / (self.max_temperature - self.min_temperature)
        )

        return speed


if __name__ == "__main__":
    controller = FanController()

    for temperature in [25, 30, 35, 40, 45, 50, 55]:
        speed = controller.calculate_speed(temperature)
        print(f"Temperature: {temperature}°C | Fan Speed: {speed * 100:.0f}%")
