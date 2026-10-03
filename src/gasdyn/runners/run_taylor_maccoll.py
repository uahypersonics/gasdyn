"""Run a configured Taylor-Maccoll calculation."""

from gasdyn.config import TaylorMaccollConfig
from gasdyn.integrations import write_taylor_maccoll_edge_state
from gasdyn.taylor_maccoll.taylor_maccoll import (
    format_taylor_maccoll_result,
    solve_taylor_maccoll,
)


def run_taylor_maccoll(config: TaylorMaccollConfig) -> str:
    """Run Taylor-Maccoll and return the formatted result.

    Args:
        config: Validated Taylor-Maccoll calculation config.

    Returns:
        Formatted text or JSON result.
    """

    # enforce the public runner contract
    if not isinstance(config, TaylorMaccollConfig):
        raise TypeError("config must be a TaylorMaccollConfig")

    # solve the configured conical flow
    result = solve_taylor_maccoll(
        mach=config.mach,
        cone_angle=config.cone_angle,
        shock_angle=config.shock_angle,
        gamma=config.gamma,
        beta_guess=config.beta_guess,
    )

    # write the optional complete dimensional edge state
    if config.upstream_state is not None and config.edge_state_output is not None:
        write_taylor_maccoll_edge_state(
            upstream_path=config.upstream_state,
            output_path=config.edge_state_output,
            result=result,
        )

    # format the result for the configured destination
    formatted = format_taylor_maccoll_result(
        result,
        as_json=config.output_format == "json",
    )

    return formatted
