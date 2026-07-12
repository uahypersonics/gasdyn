"""gasdyn - Compressible inviscid flow calculator."""

from importlib.metadata import version

__version__ = version("gasdyn")

# -- solvers --
from gasdyn.relations.isentropic import IsentropicResult, solve_isentropic
from gasdyn.relations.normal_shock import NormalShockResult, solve_normal_shock
from gasdyn.relations.oblique_shock import ObliqueResult, solve_oblique
from gasdyn.relations.prandtl_meyer import PrandtlMeyerResult, solve_prandtl_meyer
from gasdyn.taylor_maccoll.taylor_maccoll import TaylorMaccollResult, solve_taylor_maccoll

__all__ = [
    "IsentropicResult",
    "NormalShockResult",
    "ObliqueResult",
    "PrandtlMeyerResult",
    "TaylorMaccollResult",
    "solve_isentropic",
    "solve_normal_shock",
    "solve_oblique",
    "solve_prandtl_meyer",
    "solve_taylor_maccoll",
]
