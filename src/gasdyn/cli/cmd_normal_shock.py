"""CLI handler for ``gasdyn normal-shock``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import typer

from gasdyn import solve_normal_shock
from gasdyn.cli.formatters import print_result


# --------------------------------------------------
# normal-shock command
# --------------------------------------------------
def cmd_normal_shock(
    mach_1: float | None = typer.Option(None, "--mach-1", help="Upstream Mach number"),
    p_ratio: float | None = typer.Option(None, "--p-ratio", help="Pressure ratio p2/p1"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Normal shock relations."""
    try:
        result = solve_normal_shock(mach_1=mach_1, p_ratio=p_ratio, gamma=gamma)
        print_result(result, json)
    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1)
