"""Run a configured isentropic calculation."""

from gasdyn.config.config_isentropic import IsentropicConfig
from gasdyn.relations.isentropic import format_isentropic_result, solve_isentropic


def run_isentropic(config: IsentropicConfig) -> str:
    """Run isentropic relations and return the formatted result."""
    if not isinstance(config, IsentropicConfig):
        raise TypeError("config must be an IsentropicConfig")

    result = solve_isentropic(
        mach=config.mach,
        pres_ratio=config.pres_ratio,
        temp_ratio=config.temp_ratio,
        dens_ratio=config.dens_ratio,
        area_ratio=config.area_ratio,
        gamma=config.gamma,
        branch=config.branch,
    )
    formatted = format_isentropic_result(
        result,
        as_json=config.output_format == "json",
    )
    return formatted
