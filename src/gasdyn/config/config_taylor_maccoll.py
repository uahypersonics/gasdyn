"""Validated configuration for Taylor-Maccoll calculations."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gasdyn.config._converters import _optional_float, _optional_path


# --------------------------------------------------
# Taylor-Maccoll config
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class TaylorMaccollConfig:
    """Validated inputs for one Taylor-Maccoll calculation."""

    mach: float | None = None
    cone_angle: float | None = None
    shock_angle: float | None = None
    gamma: float | None = None
    beta_guess: float | None = None
    solution_output: Path | None = None
    pre_shock_state_input: Path | None = None
    post_shock_state_output: Path | None = None
    edge_state_output: Path | None = None

    def __post_init__(self) -> None:
        """Validate the configured Taylor-Maccoll calculation."""

        # validate the solver input combination
        if self.pre_shock_state_input is None:
            primary_inputs = (self.mach, self.cone_angle, self.shock_angle)
            provided = sum(value is not None for value in primary_inputs)
            if provided != 2:
                raise ValueError(
                    "[taylor_maccoll] must provide exactly two of: mach, cone_angle, shock_angle"
                )
        else:
            geometric_inputs = (self.cone_angle, self.shock_angle)
            provided = sum(value is not None for value in geometric_inputs)
            if provided != 1:
                raise ValueError(
                    "[taylor_maccoll] with pre_shock_state_input must provide "
                    "exactly one of: cone_angle, shock_angle"
                )

        # validate the gas model input
        if self.gamma is not None and self.gamma <= 1.0:
            raise ValueError("[taylor_maccoll].gamma must be greater than 1")

        # require JSON for every configured state or solution file
        json_paths = {
            "solution_output": self.solution_output,
            "pre_shock_state_input": self.pre_shock_state_input,
            "post_shock_state_output": self.post_shock_state_output,
            "edge_state_output": self.edge_state_output,
        }
        for field_name, path in json_paths.items():
            if path is not None and path.suffix.lower() != ".json":
                raise ValueError(f"[taylor_maccoll].{field_name} must use a .json file")

        # require the dimensional input and at least one dimensional output together
        has_state_input = self.pre_shock_state_input is not None
        has_state_output = (
            self.post_shock_state_output is not None or self.edge_state_output is not None
        )
        if has_state_input != has_state_output:
            raise ValueError(
                "[taylor_maccoll].pre_shock_state_input and at least one of "
                "post_shock_state_output or edge_state_output must be provided together"
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

    # define allowed/recognized keys for the [taylor_maccoll] section
    allowed_keys = {
        "mach",
        "cone_angle",
        "shock_angle",
        "gamma",
        "beta_guess",
        "solution_output",
        "pre_shock_state_input",
        "post_shock_state_output",
        "edge_state_output",
    }

    # collect all unrecognized keys
    unknown_keys = sorted(set(section) - allowed_keys)

    # if unknown keys are found, raise an error
    if unknown_keys:
        unknown = ", ".join(unknown_keys)
        raise ValueError(f"unknown [taylor_maccoll] fields: {unknown}")

    # convert TOML values into the typed config contract
    config = TaylorMaccollConfig(
        mach=_optional_float(section.get("mach")),
        cone_angle=_optional_float(section.get("cone_angle")),
        shock_angle=_optional_float(section.get("shock_angle")),
        gamma=_optional_float(section.get("gamma")),
        beta_guess=_optional_float(section.get("beta_guess")),
        solution_output=_optional_path(section.get("solution_output")),
        pre_shock_state_input=_optional_path(section.get("pre_shock_state_input")),
        post_shock_state_output=_optional_path(section.get("post_shock_state_output")),
        edge_state_output=_optional_path(section.get("edge_state_output")),
    )

    return config
