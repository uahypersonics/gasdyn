"""Run a configured normal-shock calculation."""

from gasdyn.config.config_normal_shock import NormalShockConfig
from gasdyn.relations.normal_shock import (
    format_normal_shock_result,
    solve_normal_shock,
)


def run_normal_shock(config: NormalShockConfig) -> str:
    """Run normal-shock relations and return the formatted result."""
    if not isinstance(config, NormalShockConfig):
        raise TypeError("config must be a NormalShockConfig")

    result = solve_normal_shock(
        mach_1=config.mach_1,
        pres_ratio=config.pres_ratio,
        gamma=config.gamma,
    )
    formatted = format_normal_shock_result(
        result,
        as_json=config.output_format == "json",
    )
    return formatted
