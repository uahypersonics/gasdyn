"""CLI handler for ``gasdyn taylor-maccoll``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import typer

from gasdyn.taylor_maccoll.taylor_maccoll import format_taylor_maccoll_result, solve_taylor_maccoll


# --------------------------------------------------
# taylor-maccoll command
# --------------------------------------------------
def cmd_taylor_maccoll(
    ctx: typer.Context,
    mach: float | None = typer.Option(None, "--mach", help="Freestream Mach number"),
    cone_angle: float | None = typer.Option(None, "--cone-angle", help="Cone half-angle (degrees)"),
    shock_angle: float | None = typer.Option(None, "--shock-angle", help="Shock wave angle (degrees)"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Solve Taylor-Maccoll equations."""
    # show command help when no primary solver inputs are provided
    if mach is None and cone_angle is None and shock_angle is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)

    try:
        result = solve_taylor_maccoll(
            mach=mach,
            cone_angle=cone_angle,
            shock_angle=shock_angle,
            gamma=gamma,
        )

        # print result
        typer.echo(format_taylor_maccoll_result(result, json))

    except ValueError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1)
