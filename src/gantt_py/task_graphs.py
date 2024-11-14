"""Define functions for creating and processing graphs of task dependencies."""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    from gantt_py.import_tasks import Task


def construct_task_graph(tasks: dict[str, Task]) -> nx.DiGraph:
    """Construct a directed graph to model task dependencies."""
    graph = nx.DiGraph()

    for task in tasks.values():
        graph.add_node(task.name, duration=task.duration)
        for dep_uid in task.depends_on:
            dependency = tasks.get(dep_uid)
            assert (
                dependency is not None
            ), f"Task '{task.name}' depends on invalid UID '{dep_uid}'."
            graph.add_edge(dependency.name, task.name)

    finish_node = "Finish"  # Dummy node representing when the final task ends
    graph.add_node(finish_node, duration=0)

    for task in graph.nodes:
        if graph.out_degree(task) == 0 and task != finish_node:
            graph.add_edge(task, finish_node)

    return graph


def compute_start_times(graph: nx.DiGraph) -> tuple[dict[str, int], dict[str, int]]:
    """Compute the earliest and latest valid start times for each task."""
    es_times: dict[str, int] = {node: 0 for node in graph.nodes}  # Earliest start: 0

    for node in nx.topological_sort(graph):
        for predecessor in graph.predecessors(node):
            es_times[node] = max(
                es_times[node],
                es_times[predecessor] + graph.nodes[predecessor]["duration"],
            )  # Each task must start later than all tasks directly preceding it

    finish_time = es_times["Finish"]  # Earliest possible time for all tasks to finish
    ls_times: dict[str, int] = {
        node: finish_time - graph.nodes[node]["duration"]
        for node in graph.nodes
        if node != "Finish"
    }  # All tasks must start (at latest) early enough to end by the finish time
    ls_times["Finish"] = finish_time

    for node in reversed(list(nx.topological_sort(graph))):
        for successor in graph.successors(node):
            ls_times[node] = min(
                ls_times[node],
                ls_times[successor] - graph.nodes[node]["duration"],
            )  # Each task must start early enough to finish before all following tasks

    return es_times, ls_times


def find_critical_path(
    graph: nx.DiGraph,
    es_times: dict[str, int],
    ls_times: dict[str, int],
) -> list[str]:
    """Find the tasks on the critical path using the directed graph of tasks."""
    return [n for n in nx.topological_sort(graph) if es_times[n] == ls_times[n]]
