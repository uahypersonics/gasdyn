"""CLI handler for ``gasdyn isentropic``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import typer

from gasdyn.relations.isentropic import format_isentropic_result, solve_isentropic


# --------------------------------------------------
# isentropic command
# --------------------------------------------------
def cmd_isentropic(
    mach: float | None = typer.Option(None, "--mach", help="Mach number"),
    pres_ratio: float | None = typer.Option(
        None, "--pres-ratio", help="Pressure ratio p/p0"
    ),
    temp_ratio: float | None = typer.Option(
        None, "--temp-ratio", help="Temperature ratio T/T0"
    ),
    dens_ratio: float | None = typer.Option(
        None, "--dens-ratio", help="Density ratio rho/rho0"
    ),
    area_ratio: float | None = typer.Option(None, "--area-ratio", help="Area ratio A/A*"),
    branch: str = typer.Option("supersonic", "--branch", help="Branch for area ratio (subsonic/supersonic)"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Isentropic flow relations."""
    try:
        result = solve_isentropic(
            mach=mach,
            pres_ratio=pres_ratio,
            temp_ratio=temp_ratio,
            dens_ratio=dens_ratio,
            area_ratio=area_ratio,
            gamma=gamma,
            branch=branch,
        )
        typer.echo(format_isentropic_result(result, json))
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1)
