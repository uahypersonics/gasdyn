"""Validated configuration for oblique-shock calculations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ObliqueConfig:
    """Validated inputs for one oblique-shock calculation."""

    mach: float | None = None
    deflection_angle: float | None = None
    shock_angle: float | None = None
    branch: str = "weak"
    gamma: float = 1.4
    output: Path | None = None
    output_format: str = "text"

    def __post_init__(self) -> None:
        """Validate the configured oblique-shock calculation."""
        primary_inputs = (self.mach, self.deflection_angle, self.shock_angle)
        if sum(value is not None for value in primary_inputs) != 2:
            raise ValueError(
                "[oblique] must provide exactly two of: mach, deflection_angle, shock_angle"
            )
        if self.branch not in {"weak", "strong"}:
            raise ValueError("[oblique].branch must be 'weak' or 'strong'")
        if self.gamma <= 1.0:
            raise ValueError("[oblique].gamma must be greater than 1")
        if self.output_format not in {"text", "json"}:
            raise ValueError("[oblique].format must be 'text' or 'json'")


def parse_oblique_config(section: dict[str, Any]) -> ObliqueConfig:
    """Parse and validate an ``[oblique]`` TOML section."""
    if not isinstance(section, dict):
        raise TypeError("[oblique] must be a TOML table")

    allowed_keys = {
        "mach",
        "deflection_angle",
        "shock_angle",
        "branch",
        "gamma",
        "output",
        "format",
    }
    unknown_keys = sorted(set(section) - allowed_keys)
    if unknown_keys:
        raise ValueError(f"unknown [oblique] fields: {', '.join(unknown_keys)}")

    config = ObliqueConfig(
        mach=_optional_float(section.get("mach")),
        deflection_angle=_optional_float(section.get("deflection_angle")),
        shock_angle=_optional_float(section.get("shock_angle")),
        branch=str(section.get("branch", "weak")).strip().lower(),
        gamma=float(section.get("gamma", 1.4)),
        output=_optional_path(section.get("output")),
        output_format=str(section.get("format", "text")).strip().lower(),
    )
    return config


def _optional_float(value: Any) -> float | None:
    """Convert an optional TOML value to float."""
    result = None if value is None else float(value)
    return result


def _optional_path(value: Any) -> Path | None:
    """Convert an optional TOML value to Path."""
    result = None if value is None else Path(str(value))
    return result
