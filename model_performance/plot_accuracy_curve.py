import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def build_curve(output_path: Path, show_plot: bool = False) -> None:
    sessions = [0, 10, 20, 30, 40]
    accuracy = [82.4, 84.6, 86.3, 87.2, 88.1]

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 5), dpi=140)

    ax.plot(sessions, accuracy, marker="o", linewidth=2.2)
    ax.set_title("Model Accuracy Over Sessions")
    ax.set_xlabel("Sessions")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(sessions)
    ax.set_ylim(80, 90)
    ax.grid(alpha=0.25)

    for x_value, y_value in zip(sessions, accuracy):
        ax.annotate(f"{y_value:.1f}", (x_value, y_value), textcoords="offset points", xytext=(0, 8), ha="center")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a curve graph from session-based model accuracy data."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "accuracy_curve.png",
        help="Path to save the generated chart image.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the chart window after generating the image.",
    )
    args = parser.parse_args()

    build_curve(output_path=args.output, show_plot=args.show)
    print(f"Curve graph saved to: {args.output}")


if __name__ == "__main__":
    main()