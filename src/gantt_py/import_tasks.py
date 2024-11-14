"""Define functions for importing task representations from the filesystem."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Task:
    """Each field corresponds to a column in the CSV file."""

    uid: str  # Unique identifier
    name: str
    duration: int  # Days
    depends_on: list[str]  # List of task UIDs


def from_csv(csv_path: Path) -> dict[str, Task]:
    """Read tasks from a CSV file into a map from UIDs to Task objects."""
    assert csv_path.suffix == ".csv", f"Expected CSV file; received {csv_path}."

    with Path(csv_path).open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return {
            row["UID"]: Task(
                uid=row["UID"],
                name=row["Task Name"],
                duration=int(row["Duration (days)"]),
                depends_on=row["Depends On"].split(";") if row["Depends On"] else [],
            )
            for row in reader
        }
