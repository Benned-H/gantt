"""Define functions for visualizing graphs and Gantt charts."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from plotly import graph_objects

if TYPE_CHECKING:
    from gantt_py.import_tasks import Task


def visualize_graph(graph: nx.DiGraph) -> None:
    """Visualize the given directed graph as a 2D figure."""
    # Add topological layer information for each node
    for layer_idx, nodes in enumerate(nx.topological_generations(graph)):
        for node in nodes:
            graph.nodes[node]["layer"] = layer_idx

    # Layout nodes from top to bottom based on topological depth
    pos: dict[str, np.ndarray] = {
        task: np.array([xy[0], -xy[1]])
        for task, xy in nx.multipartite_layout(
            graph,
            subset_key="layer",
            align="horizontal",
        ).items()
    }

    plt.figure(figsize=(12, 8))
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=700,
        node_color="skyblue",
        edge_color="gray",
        font_size=12,
        arrows=True,
    )

    plt.title("Task Dependency Graph")
    plt.axis("off")
    plt.show()


def plot_gantt_chart_with_slack(
    tasks: dict[str, Task],
    es_times: dict[str, int],
    ls_times: dict[str, int],
    critical_path: list[str],
) -> None:
    """Plot a Gantt chart of the given tasks, including their critical path."""
    today = pd.Timestamp.now()
    es_dates = {task: today + timedelta(days) for (task, days) in es_times.items()}
    ls_dates = {task: today + timedelta(days) for (task, days) in ls_times.items()}

    task_df = pd.DataFrame(
        [
            {
                "Task": task.name,
                "Earliest Start": es_dates[task.name],
                "Earliest Finish": es_dates[task.name] + timedelta(task.duration),
                "Latest Start": ls_dates[task.name],
                "Latest Finish": ls_dates[task.name] + timedelta(task.duration),
            }
            for task in tasks.values()
        ],
    ).sort_values(by="Earliest Start", ascending=False)

    fig = graph_objects.Figure()

    # Earliest possible schedule per task
    fig.add_trace(
        graph_objects.Bar(
            y=task_df["Task"],
            x=(task_df["Earliest Finish"] - task_df["Earliest Start"]).dt.days,
            base=(task_df["Earliest Start"] - today).dt.days,  # Days to earliest start
            name="Earliest Start",
            # marker_color=task_df["Task"].apply(
            #     lambda task: rgb_to_rgba(
            #         critical_rgb if task in critical_path else default_rgb,
            #     ),
            # ),
            orientation="h",
        ),
    )

    # Latest possible schedule per task
    fig.add_trace(
        graph_objects.Bar(
            y=task_df["Task"],
            x=(task_df["Latest Finish"] - task_df["Earliest Finish"]).dt.days,
            base=(task_df["Earliest Finish"] - today).dt.days,
            name="Latest Finish",
            # marker_color=task_df["Task"].apply(
            #     lambda task: rgb_to_rgba(
            #         pale_color(critical_rgb if task in critical_path else default_rgb),
            #     ),
            # ),
            orientation="h",
        ),
    )

    days_to_finish_date = list(range(ls_times["Finish"] + 1))
    days_to_sunday = 6 - today.weekday()  # today.weekday() gives Mon = 0 and Sun = 6

    x_labels = [
        (today + pd.Timedelta(days=i)).strftime("%m/%d/%Y")  # Full date for Sundays
        if (i - days_to_sunday) % 7 == 0
        else (today + pd.Timedelta(days=i)).strftime("%a")[0]  # Short day of the week
        for i in days_to_finish_date
    ]

    fig.update_layout(
        title="Gantt Chart with Critical Path Analysis",
        barmode="overlay",
        xaxis_title="Date",
        yaxis_title="Tasks",
        xaxis={
            "tickmode": "array",
            "tickvals": days_to_finish_date,
            "ticktext": x_labels,
        },
        showlegend=True,
    )

    fig.show()
