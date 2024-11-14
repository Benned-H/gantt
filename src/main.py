"""Read a project's tasks from CSV and render its critical path as a Gantt chart."""

import argparse
from pathlib import Path

from gantt_py.import_tasks import from_csv
from gantt_py.task_graphs import (
    compute_start_times,
    construct_task_graph,
    find_critical_path,
)
from gantt_py.visualize import plot_gantt_chart_with_slack, visualize_graph


class PathMustExistError(Exception):
    """Error representing a failed import due to an invalid provided path."""

    def __init__(self, path: Path):
        """Initialize the exception with the path found not to exist."""
        super().__init__(f"Cannot import nonexistent path {path}.")


def main(csv_path: Path) -> None:
    """Import tasks from CSV, compute their critical path, and render a Gantt chart."""
    if not csv_path.exists():
        raise PathMustExistError(csv_path)

    tasks = from_csv(csv_path)
    for task in tasks.values():
        print(task)

    graph = construct_task_graph(tasks)
    visualize_graph(graph)

    es_times, ls_times = compute_start_times(graph)
    for task in tasks.values():
        print(f"{task.name}: ES({es_times[task.name]}) LS({ls_times[task.name]})\n")

    critical_path = find_critical_path(graph, es_times, ls_times)
    print(f"Critical path: {critical_path}")

    plot_gantt_chart_with_slack(tasks, es_times, ls_times, critical_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path, help="Path to the CSV file of tasks")
    args = parser.parse_args()

    main(args.csv_path)
