"""Read a project's tasks from CSV and render its critical path as a Gantt chart."""

import argparse

import numpy as np
import pandas as pd

RGBColor = tuple[int, int, int]
default_rgb: RGBColor = (42, 25, 230)  # Blue
critical_rgb: RGBColor = (237, 2, 30)  # Red


def pale_color(color: RGBColor, pale_factor: float = 0.5) -> RGBColor:
    """Adjust color brightness by a pale factor, clipping to [0, 255]."""
    return tuple(np.clip(np.array(color) * pale_factor, 0, 255).astype(int))


def rgb_to_rgba(rgb: RGBColor, alpha: float = 0.6) -> str:
    """Convert RGB to RGBA string format for Plotly."""
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


def main(csv_file_path: str):
    tasks = read_tasks_from_csv(csv_file_path)
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
    parser.add_argument("csv_file", type=str, help="Path to the CSV file of tasks")
    args = parser.parse_args()

    main(args.csv_file)
