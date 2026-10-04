"""Validated configuration for Prandtl-Meyer calculations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gasdyn.config._converters import _optional_float, _optional_path


@dataclass(frozen=True, slots=True)
class PrandtlMeyerConfig:
    """Validated inputs for one Prandtl-Meyer calculation."""

    mach_1: float | None = None
    mach_2: float | None = None
    deflection_angle: float | None = None
    gamma: float = 1.4
    output: Path | None = None
    output_format: str = "text"

    def __post_init__(self) -> None:
        """Validate the configured Prandtl-Meyer calculation."""
        primary_inputs = (self.mach_1, self.mach_2, self.deflection_angle)
        if sum(value is not None for value in primary_inputs) != 2:
            raise ValueError(
                "[prandtl_meyer] must provide exactly two of: mach_1, mach_2, deflection_angle"
            )
        if self.gamma <= 1.0:
            raise ValueError("[prandtl_meyer].gamma must be greater than 1")
        if self.output_format not in {"text", "json"}:
            raise ValueError("[prandtl_meyer].format must be 'text' or 'json'")


def parse_prandtl_meyer_config(section: dict[str, Any]) -> PrandtlMeyerConfig:
    """Parse and validate a ``[prandtl_meyer]`` TOML section."""
    if not isinstance(section, dict):
        raise TypeError("[prandtl_meyer] must be a TOML table")

    allowed_keys = {
        "mach_1",
        "mach_2",
        "deflection_angle",
        "gamma",
        "output",
        "format",
    }
    unknown_keys = sorted(set(section) - allowed_keys)
    if unknown_keys:
        raise ValueError(f"unknown [prandtl_meyer] fields: {', '.join(unknown_keys)}")

    config = PrandtlMeyerConfig(
        mach_1=_optional_float(section.get("mach_1")),
        mach_2=_optional_float(section.get("mach_2")),
        deflection_angle=_optional_float(section.get("deflection_angle")),
        gamma=float(section.get("gamma", 1.4)),
        output=_optional_path(section.get("output")),
        output_format=str(section.get("format", "text")).strip().lower(),
    )
    return config
