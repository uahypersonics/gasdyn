"""Build canonical flow-state output from gasdyn results."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

from gasdyn.relations.oblique_shock import (
    mach_downstream_oblique,
    pres_ratio_oblique,
    temp_ratio_oblique,
)
from gasdyn.taylor_maccoll.taylor_maccoll import TaylorMaccollResult

if TYPE_CHECKING:
    from flow_state import FlowState


# --------------------------------------------------
# Taylor-Maccoll pre-shock state input
# --------------------------------------------------
def read_taylor_maccoll_pre_shock_state(path: str | Path) -> FlowState:
    """Read and validate the canonical pre-shock FlowState.

    Args:
        path: Canonical pre-shock FlowState JSON file.

    Returns:
        Complete dimensional pre-shock state.

    Raises:
        ImportError: If the optional flowstate package is not installed.
        ValueError: If the state does not contain a Mach number.
    """

    # load the optional integration only when a dimensional state is requested
    try:
        from flow_state.io import read_json
    except ImportError as exc:
        raise ImportError(
            "Taylor-Maccoll dimensional state output requires the optional flowstate "
            "package; install gasdyn[flow-state]"
        ) from exc

    # read the complete dimensional pre-shock state
    pre_shock_state = read_json(path)

    # require the flow quantity used to drive the Taylor-Maccoll solve
    if pre_shock_state.mach is None:
        raise ValueError("pre-shock FlowState must contain a Mach number")

    return pre_shock_state


# --------------------------------------------------
# Taylor-Maccoll dimensional state outputs
# --------------------------------------------------
def write_taylor_maccoll_flow_states(
    pre_shock_state: FlowState,
    pre_shock_path: str | Path,
    result: TaylorMaccollResult,
    post_shock_output_path: str | Path | None = None,
    edge_output_path: str | Path | None = None,
) -> None:
    """Build and write requested canonical Taylor-Maccoll FlowStates.

    Args:
        pre_shock_state: Complete dimensional pre-shock state.
        pre_shock_path: Canonical JSON file containing the pre-shock FlowState.
        result: Completed Taylor-Maccoll calculation.
        post_shock_output_path: Optional destination for the post-shock state.
        edge_output_path: Optional destination for the cone-edge state.

    Raises:
        ImportError: If the optional flowstate package is not installed.
        ValueError: If pre-shock Mach or gamma conflicts with the calculation.
    """

    # load the optional integration only when dimensional output is requested
    try:
        from flow_state import from_mach_pres_temp
        from flow_state.gas import get_gas
        from flow_state.io import write_json
        from flow_state.transport import transport_model_from_spec
    except ImportError as exc:
        raise ImportError(
            "Taylor-Maccoll dimensional state output requires the optional flowstate "
            "package; install gasdyn[flow-state]"
        ) from exc

    # convert to Path object for provenance
    pre_shock_path = Path(pre_shock_path)

    # validate that both packages are operating on the same pre-shock case
    if pre_shock_state.mach is None:
        raise ValueError("pre-shock FlowState must contain a Mach number")
    if not math.isclose(pre_shock_state.mach, result.mach, rel_tol=1.0e-8):
        raise ValueError(
            "pre-shock FlowState Mach does not match the Taylor-Maccoll "
            f"pre-shock Mach: {pre_shock_state.mach} != {result.mach}"
        )
    if not math.isclose(pre_shock_state.gamma, result.gamma, rel_tol=1.0e-8):
        raise ValueError(
            "pre-shock FlowState gamma does not match the Taylor-Maccoll "
            f"gamma: {pre_shock_state.gamma} != {result.gamma}"
        )

    # reconstruct the models owned by flow-state
    gas, _ = get_gas(pre_shock_state.gas_model)
    transport = None
    if pre_shock_state.transport_model is not None:
        transport = transport_model_from_spec(pre_shock_state.transport_model)

    # write the state immediately behind the conical shock when requested
    if post_shock_output_path is not None:
        shock_angle = math.radians(result.shock_angle)
        post_shock_mach = mach_downstream_oblique(result.mach, shock_angle, result.gamma)
        post_shock_pres = pre_shock_state.pres * pres_ratio_oblique(
            result.mach,
            shock_angle,
            result.gamma,
        )
        post_shock_temp = pre_shock_state.temp * temp_ratio_oblique(
            result.mach,
            shock_angle,
            result.gamma,
        )

        # build the complete post-shock state through flow-state's public solver
        post_shock_state = from_mach_pres_temp(
            mach=post_shock_mach,
            pres=post_shock_pres,
            temp=post_shock_temp,
            gas=gas,
            transport=transport,
            lref=pre_shock_state.lref,
            pr=pre_shock_state.pr,
            notes="Taylor-Maccoll post-shock state",
        )
        post_shock_state.provenance = {
            "builder": "gasdyn.taylor_maccoll",
            "state_location": "post_shock",
            "pre_shock_state_input": str(pre_shock_path),
            "pre_shock_provenance": pre_shock_state.provenance,
            "inputs": {
                "mach": result.mach,
                "shock_angle": result.shock_angle,
                "gamma": result.gamma,
            },
        }

        # write the canonical post-shock FlowState representation
        write_json(post_shock_state, post_shock_output_path)

    # write the cone-surface boundary-layer edge state when requested
    if edge_output_path is not None:
        edge_pres = pre_shock_state.pres * result.surface_pressure_ratio
        edge_temp = pre_shock_state.temp * result.surface_temp_ratio

        # build the complete edge state through flow-state's public solver
        edge_state = from_mach_pres_temp(
            mach=result.mach_cone,
            pres=edge_pres,
            temp=edge_temp,
            gas=gas,
            transport=transport,
            lref=pre_shock_state.lref,
            pr=pre_shock_state.pr,
            notes="Taylor-Maccoll cone-edge state",
        )

        # record enough provenance to reproduce the transformation
        edge_state.provenance = {
            "builder": "gasdyn.taylor_maccoll",
            "state_location": "edge",
            "pre_shock_state_input": str(pre_shock_path),
            "pre_shock_provenance": pre_shock_state.provenance,
            "inputs": {
                "mach": result.mach,
                "cone_angle": result.cone_angle,
                "shock_angle": result.shock_angle,
                "gamma": result.gamma,
                "surface_pressure_ratio": result.surface_pressure_ratio,
                "surface_temp_ratio": result.surface_temp_ratio,
            },
        }

        # write the canonical edge FlowState representation
        write_json(edge_state, edge_output_path)
