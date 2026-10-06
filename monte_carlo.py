import argparse

from scenarios.monte_carlo import run_monte_carlo


def main():
    parser = argparse.ArgumentParser(
        description="Estimate temperature-regulation uncertainty across random seeds"
    )
    parser.add_argument("--scenario", required=True, help="Path to a YAML scenario")
    parser.add_argument(
        "--runs", type=int, default=100, help="Number of simulations (default: 100)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="First random seed (defaults to the seed in the scenario)",
    )
    args = parser.parse_args()

    try:
        runs_path, summary_path, _, summary = run_monte_carlo(
            args.scenario, runs=args.runs, seed=args.seed
        )
    except ValueError as error:
        parser.error(str(error))

    print(f"Per-run results: {runs_path}")
    print(f"Uncertainty summary: {summary_path}")
    for metric, values in summary.items():
        print(
            f"{metric}: mean={values['mean']:.4f}, "
            f"SD={values['std_dev']:.4f}, "
            f"5th-95th percentile=[{values['p05']:.4f}, {values['p95']:.4f}]"
        )


if __name__ == "__main__":
    main()
