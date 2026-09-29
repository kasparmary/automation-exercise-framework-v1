"""Generic CSV reader utility.

Reads a CSV file into a list of dictionaries so it can be used directly
as Pytest parametrization input. Kept intentionally small and dependency-free
(standard library `csv` module only).
"""

import csv
from pathlib import Path


def read_csv_data(file_path: str | Path) -> list[dict[str, str]]:
    """Read a CSV file and return its rows as a list of dictionaries.

    Args:
        file_path: Path to the CSV file (absolute or relative to project root).

    Returns:
        A list of dictionaries, one per data row, keyed by the CSV header.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV test data file not found: {path}")

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)
