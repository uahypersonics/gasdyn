"""Run a configured Taylor-Maccoll calculation."""

import math

from gasdyn.config import TaylorMaccollConfig
from gasdyn.integrations import (
    read_taylor_maccoll_pre_shock_state,
    write_taylor_maccoll_flow_states,
)
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

    # resolve default standalone inputs
    resolved_mach = config.mach
    resolved_gamma = 1.4 if config.gamma is None else config.gamma
    pre_shock_state = None

    # resolve authoritative flow inputs from the optional pre-shock state
    if config.pre_shock_state_input is not None:
        pre_shock_state = read_taylor_maccoll_pre_shock_state(config.pre_shock_state_input)
        state_mach = pre_shock_state.mach
        if state_mach is None:
            raise ValueError("pre-shock FlowState must contain a Mach number")

        # validate optional explicit consistency checks before solving
        if config.mach is not None and not math.isclose(
            config.mach,
            state_mach,
            rel_tol=1.0e-8,
        ):
            raise ValueError(
                "configured Taylor-Maccoll Mach does not match the pre-shock "
                f"FlowState Mach: {config.mach} != {state_mach}"
            )
        if config.gamma is not None and not math.isclose(
            config.gamma,
            pre_shock_state.gamma,
            rel_tol=1.0e-8,
        ):
            raise ValueError(
                "configured Taylor-Maccoll gamma does not match the pre-shock "
                f"FlowState gamma: {config.gamma} != {pre_shock_state.gamma}"
            )

        # use the complete pre-shock state as the authoritative flow definition
        resolved_mach = state_mach
        resolved_gamma = pre_shock_state.gamma

    # solve the configured conical flow
    result = solve_taylor_maccoll(
        mach=resolved_mach,
        cone_angle=config.cone_angle,
        shock_angle=config.shock_angle,
        gamma=resolved_gamma,
        beta_guess=config.beta_guess,
    )

    # write the requested complete dimensional flow states
    if pre_shock_state is not None and config.pre_shock_state_input is not None:
        write_taylor_maccoll_flow_states(
            pre_shock_state=pre_shock_state,
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
