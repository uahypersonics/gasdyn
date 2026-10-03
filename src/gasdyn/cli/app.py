"""Typer application for gasdyn."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from typing import Annotated

import typer

from gasdyn.cli.callbacks import verbose_callback, version_callback
from gasdyn.cli.cmd_isentropic import isentropic_app
from gasdyn.cli.cmd_normal_shock import normal_shock_app
from gasdyn.cli.cmd_oblique import oblique_app
from gasdyn.cli.cmd_prandtl_meyer import prandtl_meyer_app
from gasdyn.cli.cmd_taylor_maccoll import taylor_maccoll_app

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
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    # --verbose -v option
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output.", callback=verbose_callback),
    ] = False,
) -> None:
    """Gas dynamics calculator."""


# --------------------------------------------------
# register commands
# --------------------------------------------------
cli.add_typer(isentropic_app, name="isentropic")
cli.add_typer(normal_shock_app, name="normal-shock")
cli.add_typer(oblique_app, name="oblique")
cli.add_typer(prandtl_meyer_app, name="prandtl-meyer")
cli.add_typer(taylor_maccoll_app, name="taylor-maccoll")

# --------------------------------------------------
# main entry point
# --------------------------------------------------
if __name__ == "__main__":
    cli()
