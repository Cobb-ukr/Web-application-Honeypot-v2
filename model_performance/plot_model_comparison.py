import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def build_chart(output_path: Path, show_plot: bool = False) -> None:
    models = ["Random Forest", "XGBoost", "CatBoost", "LightGBM", "SVM"]
    accuracies = [85, 83, 82, 81, 78]

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 5), dpi=140)

    bars = ax.bar(models, accuracies)
    ax.set_title("Comparative Performance of Classification Models")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(0, 100)

    for bar, accuracy in zip(bars, accuracies):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{accuracy}%",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a model accuracy comparison graph from the thesis table."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "model_comparison.png",
        help="Path to save the generated chart image.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the chart window after generating the image.",
    )
    args = parser.parse_args()

    build_chart(output_path=args.output, show_plot=args.show)
    print(f"Chart saved to: {args.output}")


if __name__ == "__main__":
    main()