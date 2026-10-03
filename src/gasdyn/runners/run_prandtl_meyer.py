"""Run a configured Prandtl-Meyer calculation."""

from gasdyn.config.config_prandtl_meyer import PrandtlMeyerConfig
from gasdyn.relations.prandtl_meyer import (
    format_prandtl_meyer_result,
    solve_prandtl_meyer,
)


def run_prandtl_meyer(config: PrandtlMeyerConfig) -> str:
    """Run Prandtl-Meyer relations and return the formatted result."""
    if not isinstance(config, PrandtlMeyerConfig):
        raise TypeError("config must be a PrandtlMeyerConfig")

    result = solve_prandtl_meyer(
        mach_1=config.mach_1,
        mach_2=config.mach_2,
        deflection_angle=config.deflection_angle,
        gamma=config.gamma,
    )
    formatted = format_prandtl_meyer_result(
        result,
        as_json=config.output_format == "json",
    )
    return formatted
