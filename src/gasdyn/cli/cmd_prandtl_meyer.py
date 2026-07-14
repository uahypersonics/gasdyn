"""CLI handler for ``gasdyn prandtl-meyer``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import typer

from gasdyn.relations.prandtl_meyer import format_prandtl_meyer_result, solve_prandtl_meyer


# --------------------------------------------------
# prandtl-meyer command
# --------------------------------------------------
def cmd_prandtl_meyer(
    mach_1: float | None = typer.Option(None, "--mach-1", help="Upstream Mach number"),
    mach_2: float | None = typer.Option(None, "--mach-2", help="Downstream Mach number"),
    deflection_angle: float | None = typer.Option(None, "--deflection-angle", help="Flow deflection angle (degrees)"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Prandtl-Meyer expansion."""
    try:
        result = solve_prandtl_meyer(
            mach_1=mach_1,
            mach_2=mach_2,
            deflection_angle=deflection_angle,
            gamma=gamma,
        )
        typer.echo(format_prandtl_meyer_result(result, json))
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1)
