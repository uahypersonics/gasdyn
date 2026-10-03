"""Validated configuration for isentropic calculations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class IsentropicConfig:
    """Validated inputs for one isentropic calculation."""

    mach: float | None = None
    pres_ratio: float | None = None
    temp_ratio: float | None = None
    dens_ratio: float | None = None
    area_ratio: float | None = None
    branch: str = "supersonic"
    gamma: float = 1.4
    output: Path | None = None
    output_format: str = "text"

    def __post_init__(self) -> None:
        """Validate the configured isentropic calculation."""
        primary_inputs = (
            self.mach,
            self.pres_ratio,
            self.temp_ratio,
            self.dens_ratio,
            self.area_ratio,
        )
        if sum(value is not None for value in primary_inputs) != 1:
            raise ValueError(
                "[isentropic] must provide exactly one of: mach, pres_ratio, "
                "temp_ratio, dens_ratio, area_ratio"
            )
        if self.branch not in {"subsonic", "supersonic"}:
            raise ValueError("[isentropic].branch must be 'subsonic' or 'supersonic'")
        if self.gamma <= 1.0:
            raise ValueError("[isentropic].gamma must be greater than 1")
        if self.output_format not in {"text", "json"}:
            raise ValueError("[isentropic].format must be 'text' or 'json'")


def parse_isentropic_config(section: dict[str, Any]) -> IsentropicConfig:
    """Parse and validate an ``[isentropic]`` TOML section."""
    if not isinstance(section, dict):
        raise TypeError("[isentropic] must be a TOML table")

    allowed_keys = {
        "mach",
        "pres_ratio",
        "temp_ratio",
        "dens_ratio",
        "area_ratio",
        "branch",
        "gamma",
        "output",
        "format",
    }
    unknown_keys = sorted(set(section) - allowed_keys)
    if unknown_keys:
        raise ValueError(f"unknown [isentropic] fields: {', '.join(unknown_keys)}")

    config = IsentropicConfig(
        mach=_optional_float(section.get("mach")),
        pres_ratio=_optional_float(section.get("pres_ratio")),
        temp_ratio=_optional_float(section.get("temp_ratio")),
        dens_ratio=_optional_float(section.get("dens_ratio")),
        area_ratio=_optional_float(section.get("area_ratio")),
        branch=str(section.get("branch", "supersonic")).strip().lower(),
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
