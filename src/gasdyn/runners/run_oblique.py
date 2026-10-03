"""Run a configured oblique-shock calculation."""

from gasdyn.config.config_oblique import ObliqueConfig
from gasdyn.relations.oblique_shock import format_oblique_result, solve_oblique


def run_oblique(config: ObliqueConfig) -> str:
    """Run oblique-shock relations and return the formatted result."""
    if not isinstance(config, ObliqueConfig):
        raise TypeError("config must be an ObliqueConfig")

    result = solve_oblique(
        mach=config.mach,
        deflection_angle=config.deflection_angle,
        shock_angle=config.shock_angle,
        gamma=config.gamma,
        branch=config.branch,
    )
    formatted = format_oblique_result(
        result,
        as_json=config.output_format == "json",
    )
    return formatted
