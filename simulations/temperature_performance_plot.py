
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulations"))

from sensor_fault_simulation import simulate


def main():
    history = simulate()

    time = [point["time"] for point in history]
    temperature = [
        point["actual_temperature"] for point in history
    ]
    fan_speed = [
        point["fan_speed"] * 100 for point in history
    ]

    fig, ax1 = plt.subplots(figsize=(11, 6))

    ax1.plot(
        time,
        temperature,
        label="Actual Temperature",
        linewidth=2,
        color="red",
    )

    ax1.axhline(
        40.0,
        color="green",
        linestyle="--",
        label="Target Temperature (40°C)",
    )

    ax1.axvspan(
        200, 250,
        color="orange",
        alpha=0.2,
        label="Sensor Failure",
    )

    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()

    ax2.plot(
        time,
        fan_speed,
        color="blue",
        alpha=0.65,
        label="Fan Speed",
    )

    ax2.set_ylabel("Fan Speed (%)")
    ax2.set_ylim(0, 110)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper left",
    )

    plt.title(
        "Intelligent Fan: Temperature Control and Sensor Fault Recovery"
    )

    fig.tight_layout()

    output = ROOT / "results" / "temperature_performance.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output, dpi=200)
    print(f"Graph saved to: {output}")

    plt.show()


if __name__ == "__main__":
    main()
