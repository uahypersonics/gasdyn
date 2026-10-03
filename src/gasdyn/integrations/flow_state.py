"""Build canonical flow-state output from gasdyn results."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import math
from pathlib import Path

from gasdyn.taylor_maccoll.taylor_maccoll import TaylorMaccollResult


# --------------------------------------------------
# Taylor-Maccoll edge-state output
# --------------------------------------------------
def write_taylor_maccoll_edge_state(
    upstream_path: str | Path,
    output_path: str | Path,
    result: TaylorMaccollResult,
) -> None:
    """Build and write a canonical cone-edge FlowState.

    Args:
        upstream_path: Canonical JSON file containing the upstream FlowState.
        output_path: Destination for the canonical edge-state JSON file.
        result: Completed Taylor-Maccoll calculation.

    Raises:
        ImportError: If the optional flowstate package is not installed.
        ValueError: If upstream Mach or gamma conflicts with the calculation.
    """

    # load the optional integration only when edge-state output is requested
    try:
        from flow_state import from_mach_pres_temp
        from flow_state.gas import get_gas
        from flow_state.io import read_json, write_json
        from flow_state.transport import transport_model_from_spec
    except ImportError as exc:
        raise ImportError(
            "Taylor-Maccoll edge-state output requires the optional flowstate "
            "package; install gasdyn[flow-state]"
        ) from exc

    # read the complete dimensional upstream state
    upstream_path = Path(upstream_path)
    upstream_state = read_json(upstream_path)

    # validate that both packages are operating on the same freestream case
    if upstream_state.mach is None:
        raise ValueError("upstream FlowState must contain a Mach number")
    if not math.isclose(upstream_state.mach, result.mach, rel_tol=1.0e-8):
        raise ValueError(
            "upstream FlowState Mach does not match the Taylor-Maccoll "
            f"freestream Mach: {upstream_state.mach} != {result.mach}"
        )
    if not math.isclose(upstream_state.gamma, result.gamma, rel_tol=1.0e-8):
        raise ValueError(
            "upstream FlowState gamma does not match the Taylor-Maccoll "
            f"gamma: {upstream_state.gamma} != {result.gamma}"
        )

    # reconstruct the models owned by flow-state
    gas, _ = get_gas(upstream_state.gas_model)
    transport = None
    if upstream_state.transport_model is not None:
        transport = transport_model_from_spec(upstream_state.transport_model)

    # dimensionalize the Taylor-Maccoll cone-surface ratios
    edge_pres = upstream_state.pres * result.surface_pressure_ratio
    edge_temp = upstream_state.temp * result.surface_temp_ratio

    # build a complete state through flow-state's public solver
    edge_state = from_mach_pres_temp(
        mach=result.mach_cone,
        pres=edge_pres,
        temp=edge_temp,
        gas=gas,
        transport=transport,
        lref=upstream_state.lref,
        pr=upstream_state.pr,
        notes="Taylor-Maccoll cone-edge state",
    )

    # record enough provenance to reproduce the transformation
    edge_state.provenance = {
        "builder": "gasdyn.taylor_maccoll",
        "upstream_state": str(upstream_path),
        "upstream_provenance": upstream_state.provenance,
        "inputs": {
            "mach": result.mach,
            "cone_angle": result.cone_angle,
            "shock_angle": result.shock_angle,
            "gamma": result.gamma,
            "surface_pressure_ratio": result.surface_pressure_ratio,
            "surface_temp_ratio": result.surface_temp_ratio,
        },
    }

    # write the canonical FlowState representation
    write_json(edge_state, output_path)
