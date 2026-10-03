"""Configured gasdyn calculation runners."""

from gasdyn.runners.run_isentropic import run_isentropic
from gasdyn.runners.run_normal_shock import run_normal_shock
from gasdyn.runners.run_oblique import run_oblique
from gasdyn.runners.run_prandtl_meyer import run_prandtl_meyer
from gasdyn.runners.run_taylor_maccoll import run_taylor_maccoll

__all__ = [
    "run_isentropic",
    "run_normal_shock",
    "run_oblique",
    "run_prandtl_meyer",
    "run_taylor_maccoll",
]
