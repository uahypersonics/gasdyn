"""Validated configuration for Taylor-Maccoll calculations."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


# --------------------------------------------------
# Taylor-Maccoll config
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class TaylorMaccollConfig:
    """Validated inputs for one Taylor-Maccoll calculation."""

    mach: float | None = None
    cone_angle: float | None = None
    shock_angle: float | None = None
    gamma: float = 1.4
    beta_guess: float | None = None
    output: Path | None = None
    output_format: str = "text"
    upstream_state: Path | None = None
    edge_state_output: Path | None = None

    def __post_init__(self) -> None:
        """Validate the configured Taylor-Maccoll calculation."""

        # validate the solver input combination
        primary_inputs = (self.mach, self.cone_angle, self.shock_angle)
        provided = sum(value is not None for value in primary_inputs)
        if provided != 2:
            raise ValueError(
                "[taylor_maccoll] must provide exactly two of: mach, cone_angle, shock_angle"
            )

        # validate common gas and output settings
        if self.gamma <= 1.0:
            raise ValueError("[taylor_maccoll].gamma must be greater than 1")
        if self.output_format not in {"text", "json"}:
            raise ValueError("[taylor_maccoll].format must be 'text' or 'json'")

        # require both paths so edge-state generation is explicit and complete
        edge_paths = (self.upstream_state, self.edge_state_output)
        if sum(path is not None for path in edge_paths) == 1:
            raise ValueError(
                "[taylor_maccoll].upstream_state and edge_state_output must be provided together"
            )


# --------------------------------------------------
# config parser
# --------------------------------------------------
def parse_taylor_maccoll_config(section: dict[str, Any]) -> TaylorMaccollConfig:
    """Parse and validate a ``[taylor_maccoll]`` TOML section.

    Args:
        section: Parsed TOML section.

    Returns:
        Validated Taylor-Maccoll config.

    Raises:
        TypeError: If the section is not a TOML table.
        ValueError: If fields are unknown or invalid.
    """

    # validate section type and keys
    if not isinstance(section, dict):
        raise TypeError("[taylor_maccoll] must be a TOML table")

    allowed_keys = {
        "mach",
        "cone_angle",
        "shock_angle",
        "gamma",
        "beta_guess",
        "output",
        "format",
        "upstream_state",
        "edge_state_output",
    }
    unknown_keys = sorted(set(section) - allowed_keys)
    if unknown_keys:
        unknown = ", ".join(unknown_keys)
        raise ValueError(f"unknown [taylor_maccoll] fields: {unknown}")

    # convert TOML values into the typed config contract
    config = TaylorMaccollConfig(
        mach=_optional_float(section.get("mach")),
        cone_angle=_optional_float(section.get("cone_angle")),
        shock_angle=_optional_float(section.get("shock_angle")),
        gamma=float(section.get("gamma", 1.4)),
        beta_guess=_optional_float(section.get("beta_guess")),
        output=_optional_path(section.get("output")),
        output_format=str(section.get("format", "text")).strip().lower(),
        upstream_state=_optional_path(section.get("upstream_state")),
        edge_state_output=_optional_path(section.get("edge_state_output")),
    )

    return config


# --------------------------------------------------
# value conversion helpers
# --------------------------------------------------
def _optional_float(value: Any) -> float | None:
    """Convert an optional TOML value to float."""
    result = None if value is None else float(value)
    return result


def _optional_path(value: Any) -> Path | None:
    """Convert an optional TOML value to Path."""
    result = None if value is None else Path(str(value))
    return result
