"""CLI handler for ``gasdyn prandtl-meyer``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import typer

from gasdyn.config import (
    DEFAULT_CONFIG_PATH,
    PRANDTL_MEYER_TEMPLATE,
    PrandtlMeyerConfig,
    parse_prandtl_meyer_config,
    read_config,
    write_config,
)
from gasdyn.runners import run_prandtl_meyer

prandtl_meyer_app = typer.Typer(
    name="prandtl-meyer",
    help="Prandtl-Meyer expansion relations.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@prandtl_meyer_app.callback()
def prandtl_meyer_callback(ctx: typer.Context) -> None:
    """Show Prandtl-Meyer help when no action is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


# --------------------------------------------------
# prandtl-meyer command
# --------------------------------------------------
@prandtl_meyer_app.command(name="run")
def cmd_prandtl_meyer(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file. Defaults to gasdyn.toml."
    ),
    mach_1: float | None = typer.Option(None, "--mach-1", help="Upstream Mach number"),
    mach_2: float | None = typer.Option(None, "--mach-2", help="Downstream Mach number"),
    deflection_angle: float | None = typer.Option(None, "--deflection-angle", help="Flow deflection angle (degrees)"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write the result to a file."
    ),
) -> None:
    """Prandtl-Meyer expansion."""
    direct_inputs = (mach_1, mach_2, deflection_angle)
    use_direct_options = any(value is not None for value in direct_inputs)

    try:
        if use_direct_options:
            if config is not None:
                raise ValueError("--config cannot be combined with direct solver inputs")
            calculation = PrandtlMeyerConfig(
                mach_1=mach_1,
                mach_2=mach_2,
                deflection_angle=deflection_angle,
                gamma=gamma,
                output=output,
                output_format="json" if json else "text",
            )
        else:
            config_data = read_config(config)
            if "prandtl_meyer" not in config_data:
                config_path = DEFAULT_CONFIG_PATH if config is None else config
                raise ValueError(
                    f"config does not contain [prandtl_meyer]: {config_path}"
                )
            calculation = parse_prandtl_meyer_config(
                config_data["prandtl_meyer"]
            )

        formatted = run_prandtl_meyer(calculation)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    if calculation.output is None:
        typer.echo(formatted)
    else:
        calculation.output.write_text(formatted + "\n", encoding="utf-8")
        typer.echo(f"Written: {calculation.output}")


@prandtl_meyer_app.command(name="init")
def cmd_init_prandtl_meyer(
    output: Path = typer.Option(DEFAULT_CONFIG_PATH, "--output", "-o"),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """Write a focused Prandtl-Meyer config file."""
    try:
        config_path = write_config(PRANDTL_MEYER_TEMPLATE, output, force=force)
    except FileExistsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Written: {config_path}")
    typer.echo(f"Then run: gasdyn prandtl-meyer run --config {config_path}")
