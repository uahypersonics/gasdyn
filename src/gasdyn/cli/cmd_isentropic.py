"""CLI handler for ``gasdyn isentropic``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import typer

from gasdyn.config import (
    DEFAULT_CONFIG_PATH,
    ISENTROPIC_TEMPLATE,
    IsentropicConfig,
    parse_isentropic_config,
    read_config,
    write_config,
)
from gasdyn.runners import run_isentropic

# --------------------------------------------------
# isentropic command group
# --------------------------------------------------
isentropic_app = typer.Typer(
    name="isentropic",
    help="Isentropic flow relations.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@isentropic_app.callback()
def isentropic_callback(ctx: typer.Context) -> None:
    """Show isentropic help when no action is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


# --------------------------------------------------
# isentropic command
# --------------------------------------------------
@isentropic_app.command(name="run")
def cmd_isentropic(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file. Defaults to gasdyn.toml."
    ),
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
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write the result to a file."
    ),
) -> None:
    """Isentropic flow relations."""
    direct_inputs = (mach, pres_ratio, temp_ratio, dens_ratio, area_ratio)
    use_direct_options = any(value is not None for value in direct_inputs)

    try:
        if use_direct_options:
            if config is not None:
                raise ValueError("--config cannot be combined with direct solver inputs")
            calculation = IsentropicConfig(
                mach=mach,
                pres_ratio=pres_ratio,
                temp_ratio=temp_ratio,
                dens_ratio=dens_ratio,
                area_ratio=area_ratio,
                branch=branch,
                gamma=gamma,
                output=output,
                output_format="json" if json else "text",
            )
        else:
            config_data = read_config(config)
            if "isentropic" not in config_data:
                config_path = DEFAULT_CONFIG_PATH if config is None else config
                raise ValueError(f"config does not contain [isentropic]: {config_path}")
            calculation = parse_isentropic_config(config_data["isentropic"])

        formatted = run_isentropic(calculation)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    if calculation.output is None:
        typer.echo(formatted)
    else:
        calculation.output.write_text(formatted + "\n", encoding="utf-8")
        typer.echo(f"Written: {calculation.output}")


@isentropic_app.command(name="init")
def cmd_init_isentropic(
    output: Path = typer.Option(DEFAULT_CONFIG_PATH, "--output", "-o"),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """Write a focused isentropic config file."""
    try:
        config_path = write_config(ISENTROPIC_TEMPLATE, output, force=force)
    except FileExistsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Written: {config_path}")
    typer.echo(f"Then run: gasdyn isentropic run --config {config_path}")
