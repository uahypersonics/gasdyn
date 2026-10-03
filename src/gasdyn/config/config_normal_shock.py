"""Validated configuration for normal-shock calculations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class NormalShockConfig:
    """Validated inputs for one normal-shock calculation."""

    mach_1: float | None = None
    pres_ratio: float | None = None
    gamma: float = 1.4
    output: Path | None = None
    output_format: str = "text"

    def __post_init__(self) -> None:
        """Validate the configured normal-shock calculation."""
        if sum(value is not None for value in (self.mach_1, self.pres_ratio)) != 1:
            raise ValueError(
                "[normal_shock] must provide exactly one of: mach_1, pres_ratio"
            )
        if self.gamma <= 1.0:
            raise ValueError("[normal_shock].gamma must be greater than 1")
        if self.output_format not in {"text", "json"}:
            raise ValueError("[normal_shock].format must be 'text' or 'json'")


def parse_normal_shock_config(section: dict[str, Any]) -> NormalShockConfig:
    """Parse and validate a ``[normal_shock]`` TOML section."""
    if not isinstance(section, dict):
        raise TypeError("[normal_shock] must be a TOML table")

    allowed_keys = {"mach_1", "pres_ratio", "gamma", "output", "format"}
    unknown_keys = sorted(set(section) - allowed_keys)
    if unknown_keys:
        raise ValueError(f"unknown [normal_shock] fields: {', '.join(unknown_keys)}")

    config = NormalShockConfig(
        mach_1=_optional_float(section.get("mach_1")),
        pres_ratio=_optional_float(section.get("pres_ratio")),
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
