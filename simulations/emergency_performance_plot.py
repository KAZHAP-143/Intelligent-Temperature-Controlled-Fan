
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "simulations"))

from emergency_safety_simulation import simulate


def main():
    history = simulate()

    time = [point["time"] for point in history]
    temperature = [point["temperature"] for point in history]
    fan_speed = [point["fan_speed"] * 100 for point in history]

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(
        time,
        temperature,
        color="red",
        linewidth=2,
        label="Actual Temperature",
    )

    ax1.axhline(
        40,
        color="green",
        linestyle="--",
        label="Target (40°C)",
    )

    ax1.axhline(
        50,
        color="orange",
        linestyle="--",
        label="Warning (50°C)",
    )

    ax1.axhline(
        55,
        color="darkred",
        linestyle="--",
        label="Critical (55°C)",
    )

    # High heat input occurs between 120s and 360s.
    ax1.axvspan(
        120,
        360,
        color="orange",
        alpha=0.12,
        label="400 W Heat Load",
    )

    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Temperature (°C)")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()

    ax2.plot(
        time,
        fan_speed,
        color="blue",
        linewidth=1.5,
        alpha=0.7,
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
        fontsize=9,
    )

    plt.title("Emergency Overheating and Thermal Safety Response")
    fig.tight_layout()

    output = ROOT / "results" / "emergency_performance.png"
    output.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output, dpi=200)
    print(f"Graph saved to: {output}")

    plt.show()


if __name__ == "__main__":
    main()
