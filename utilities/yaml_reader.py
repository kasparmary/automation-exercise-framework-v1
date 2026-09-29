"""Generic YAML configuration reader utility."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml_config(file_path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary.

    Args:
        file_path: Path to the YAML file (absolute or relative to project root).

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"YAML config file not found: {path}")

    with path.open(encoding="utf-8") as yaml_file:
        return yaml.safe_load(yaml_file) or {}
