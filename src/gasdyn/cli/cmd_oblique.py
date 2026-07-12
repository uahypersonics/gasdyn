"""CLI handler for ``gasdyn oblique``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import typer

from gasdyn import solve_oblique
from gasdyn.cli.formatters import print_result


# --------------------------------------------------
# oblique command
# --------------------------------------------------
def cmd_oblique(
    mach: float | None = typer.Option(None, "--mach", help="Upstream Mach number"),
    deflection_angle: float | None = typer.Option(None, "--deflection-angle", help="Flow deflection angle (degrees)"),
    shock_angle: float | None = typer.Option(None, "--shock-angle", help="Shock wave angle (degrees)"),
    branch: str = typer.Option("weak", "--branch", help="Shock branch (weak/strong)"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Oblique shock relations."""
    try:
        result = solve_oblique(
            mach=mach,
            deflection_angle=deflection_angle,
            shock_angle=shock_angle,
            gamma=gamma,
            branch=branch,
        )
        print_result(result, json)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1)
