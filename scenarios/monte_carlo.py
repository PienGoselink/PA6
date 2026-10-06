import csv
import os
import statistics
import time
from typing import Dict, List, Optional, Tuple

from utils.config import load_config
from scenarios.runner import simulate_scenario


Metric = Dict[str, float]
RunMetric = Dict[str, float | int]


def calculate_metrics(log: Dict[str, List[float]]) -> Metric:
    """Calculate regulation and heater-use metrics for one simulation run."""
    if not log["T_true"]:
        raise ValueError("Cannot calculate metrics for an empty simulation log")

    errors = [
        temperature - setpoint
        for temperature, setpoint in zip(log["T_true"], log["setpoint"])
    ]
    heater = log["heater"]
    count = len(errors)
    return {
        "duty_cycle_percent": 100.0 * sum(heater) / len(heater),
        "mean_abs_error_C": sum(abs(error) for error in errors) / count,
        "rmse_C": (sum(error ** 2 for error in errors) / count) ** 0.5,
        "min_temperature_C": min(log["T_true"]),
        "max_temperature_C": max(log["T_true"]),
    }


def _percentile(values: List[float], percentile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[upper] - ordered[lower])


def run_monte_carlo(
    scenario_path: str,
    runs: int = 100,
    seed: Optional[int] = None,
    output_dir: str = os.path.join("outputs", "monte_carlo"),
) -> Tuple[str, str, List[RunMetric], Dict[str, Metric]]:
    """Run a scenario with consecutive seeds and write run and summary CSVs."""
    if runs < 2:
        raise ValueError("At least two runs are required to estimate uncertainty")

    config = load_config(scenario_path)
    first_seed = config.sim.seed if seed is None else seed
    run_metrics: List[RunMetric] = []
    for index in range(runs):
        log, _ = simulate_scenario(scenario_path, seed=first_seed + index)
        metrics = calculate_metrics(log)
        run_metrics.append({"seed": first_seed + index, **metrics})

    metric_names = list(run_metrics[0])
    metric_names.remove("seed")
    summary: Dict[str, Metric] = {}
    for name in metric_names:
        values = [float(run[name]) for run in run_metrics]
        summary[name] = {
            "mean": statistics.mean(values),
            "std_dev": statistics.stdev(values),
            "p05": _percentile(values, 0.05),
            "p95": _percentile(values, 0.95),
        }

    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    scenario_name = os.path.splitext(os.path.basename(scenario_path))[0]
    runs_path = os.path.join(output_dir, f"{scenario_name}-runs-{timestamp}.csv")
    summary_path = os.path.join(
        output_dir, f"{scenario_name}-summary-{timestamp}.csv"
    )

    with open(runs_path, "w", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["seed", *metric_names])
        writer.writeheader()
        writer.writerows(run_metrics)

    with open(summary_path, "w", newline="") as output_file:
        fieldnames = ["metric", "mean", "std_dev", "p05", "p95"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for name, values in summary.items():
            writer.writerow({"metric": name, **values})

    return runs_path, summary_path, run_metrics, summary
