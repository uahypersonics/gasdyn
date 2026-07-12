"""Typer application for gasdyn."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from typing import Annotated

import typer

from gasdyn.cli.callbacks import verbose_callback, version_callback
from gasdyn.cli.cmd_isentropic import cmd_isentropic
from gasdyn.cli.cmd_normal_shock import cmd_normal_shock
from gasdyn.cli.cmd_oblique import cmd_oblique
from gasdyn.cli.cmd_prandtl_meyer import cmd_prandtl_meyer
from gasdyn.cli.cmd_taylor_maccoll import cmd_taylor_maccoll

# --------------------------------------------------
# build the app
# --------------------------------------------------
cli = typer.Typer(
    name="gasdyn",
    help="Gas dynamics calculator",
    no_args_is_help=True,
    add_completion=False,
)

# --------------------------------------------------
# global options via callback
# --------------------------------------------------
@cli.callback()
def callback(
    # --version -V option
    version: Annotated[
        bool | None,
        typer.Option("--version", "-V",
                     help="Show version and exit.",
                     callback=version_callback,
                     is_eager=True
                    ),
    ] = None,
    # --verbose -v option
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v",
                     help="Enable informational output.",
                     callback=verbose_callback
                    ),
    ] = False,
) -> None:
    """Gas dynamics calculator."""

# --------------------------------------------------
# register commands
# --------------------------------------------------
cli.command(name="isentropic")(cmd_isentropic)
cli.command(name="normal-shock")(cmd_normal_shock)
cli.command(name="oblique")(cmd_oblique)
cli.command(name="prandtl-meyer")(cmd_prandtl_meyer)
cli.command(name="taylor-maccoll")(cmd_taylor_maccoll)

# --------------------------------------------------
# main entry point
# --------------------------------------------------
if __name__ == "__main__":
    cli()
