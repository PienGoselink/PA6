import csv

import pytest

from scenarios.monte_carlo import calculate_metrics, run_monte_carlo


def test_calculate_metrics():
    log = {
        "T_true": [20.0, 22.0],
        "setpoint": [21.0, 21.0],
        "heater": [1.0, 0.0],
    }

    metrics = calculate_metrics(log)

    assert metrics["duty_cycle_percent"] == 50.0
    assert metrics["mean_abs_error_C"] == 1.0
    assert metrics["rmse_C"] == 1.0
    assert metrics["min_temperature_C"] == 20.0
    assert metrics["max_temperature_C"] == 22.0


def test_run_monte_carlo_writes_per_run_and_summary_csvs(tmp_path):
    scenario_path = tmp_path / "small_scenario.yaml"
    scenario_path.write_text(
        """\
env:
  base: 5.0
  amplitude: 0.0
  period_s: 100.0
  door_drop_C: 0.0
  door_start_s: 10.0
  door_duration_s: 2.0
sensor:
  sigma: 0.2
  bias: 0.0
  dropout_prob: 0.0
controller:
  type: onoff
  setpoint: 21.0
  deadband: 1.0
  safety_high: 26.0
model:
  R: 0.5
  C: 10000.0
  P: 200.0
  process_sigma: 0.1
sim:
  dt: 1.0
  duration_s: 20.0
  seed: 10
  init_T: 18.0
""",
        encoding="utf-8",
    )

    runs_path, summary_path, run_metrics, summary = run_monte_carlo(
        str(scenario_path), runs=3, output_dir=str(tmp_path / "results")
    )

    assert [int(run["seed"]) for run in run_metrics] == [10, 11, 12]
    assert len(summary) == 5
    with open(runs_path, newline="", encoding="utf-8") as output_file:
        saved_runs = list(csv.DictReader(output_file))
    with open(summary_path, newline="", encoding="utf-8") as output_file:
        saved_summary = list(csv.DictReader(output_file))
    assert [int(run["seed"]) for run in saved_runs] == [10, 11, 12]
    assert len(saved_summary) == 5


def test_run_monte_carlo_requires_two_runs(tmp_path):
    with pytest.raises(ValueError, match="At least two runs"):
        run_monte_carlo("unused.yaml", runs=1, output_dir=str(tmp_path))


def test_calculate_metrics_rejects_empty_log():
    with pytest.raises(ValueError, match="empty simulation log"):
        calculate_metrics({"T_true": [], "setpoint": [], "heater": []})
