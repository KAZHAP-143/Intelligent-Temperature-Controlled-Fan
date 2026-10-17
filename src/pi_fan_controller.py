
class PIFanController:
    """PI temperature controller with integral anti-windup."""

    def __init__(
        self,
        target_temperature=40.0,
        kp=0.08,
        ki=0.002,
    ):
        if kp < 0 or ki < 0:
            raise ValueError("Controller gains cannot be negative.")

        self.target_temperature = target_temperature
        self.kp = kp
        self.ki = ki
        self.integral = 0.0

    def calculate_speed(self, temperature, time_step=1.0):
        """Calculate normalized fan speed between 0 and 1."""

        if time_step <= 0:
            raise ValueError("Time step must be positive.")

        # Positive error means the system is too hot.
        error = temperature - self.target_temperature

        proposed_integral = self.integral + error * time_step

        unsaturated_speed = (
            self.kp * error + self.ki * proposed_integral
        )

        speed = max(0.0, min(1.0, unsaturated_speed))

        # Conditional integration prevents further saturation.
        if (
            0.0 <= unsaturated_speed <= 1.0
            or (unsaturated_speed > 1.0 and error < 0)
            or (unsaturated_speed < 0.0 and error > 0)
        ):
            self.integral = proposed_integral

        return speed

    def reset(self):
        """Reset integral state."""
        self.integral = 0.0


if __name__ == "__main__":
    controller = PIFanController()

    for temperature in [35, 38, 40, 42, 45, 50]:
        controller.reset()
        speed = controller.calculate_speed(temperature)

        print(
            f"Temperature: {temperature}°C | "
            f"Fan Speed: {speed * 100:.1f}%"
        )
