"""Shared value converters for gasdyn configuration parsers."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Any


# --------------------------------------------------
# optional value converters
# --------------------------------------------------
def _optional_float(value: Any) -> float | None:
    """Convert an optional TOML value to float."""
    result = None if value is None else float(value)
    return result


def _optional_path(value: Any) -> Path | None:
    """Convert an optional TOML value to Path."""
    result = None if value is None else Path(str(value))
    return result
