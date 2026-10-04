"""Run a configured Taylor-Maccoll calculation."""

from gasdyn.config import TaylorMaccollConfig
from gasdyn.integrations import write_taylor_maccoll_flow_states
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

    # write the requested complete dimensional flow states
    if config.pre_shock_state_input is not None:
        write_taylor_maccoll_flow_states(
            pre_shock_path=config.pre_shock_state_input,
            result=result,
            post_shock_output_path=config.post_shock_state_output,
            edge_output_path=config.edge_state_output,
        )

    # infer JSON from the configured solution filename; otherwise return terminal text
    formatted = format_taylor_maccoll_result(
        result,
        as_json=config.solution_output is not None,
    )

    return formatted
