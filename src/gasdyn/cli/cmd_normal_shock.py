"""CLI handler for ``gasdyn normal-shock``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import typer

from gasdyn.config import (
    DEFAULT_CONFIG_PATH,
    NORMAL_SHOCK_TEMPLATE,
    NormalShockConfig,
    parse_normal_shock_config,
    read_config,
    write_config,
)
from gasdyn.runners import run_normal_shock

# --------------------------------------------------
# normal-shock command group
# --------------------------------------------------
normal_shock_app = typer.Typer(
    name="normal-shock",
    help="Normal-shock flow relations.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@normal_shock_app.callback()
def normal_shock_callback(ctx: typer.Context) -> None:
    """Show normal-shock help when no action is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


# --------------------------------------------------
# normal-shock command
# --------------------------------------------------
@normal_shock_app.command(name="run")
def cmd_normal_shock(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file. Defaults to gasdyn.toml."
    ),
    mach_1: float | None = typer.Option(None, "--mach-1", help="Upstream Mach number"),
    pres_ratio: float | None = typer.Option(
        None, "--pres-ratio", help="Pressure ratio p2/p1"
    ),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write the result to a file."
    ),
) -> None:
    """Normal shock relations."""
    use_direct_options = mach_1 is not None or pres_ratio is not None

    try:
        if use_direct_options:
            if config is not None:
                raise ValueError("--config cannot be combined with direct solver inputs")
            calculation = NormalShockConfig(
                mach_1=mach_1,
                pres_ratio=pres_ratio,
                gamma=gamma,
                output=output,
                output_format="json" if json else "text",
            )
        else:
            config_data = read_config(config)
            if "normal_shock" not in config_data:
                config_path = DEFAULT_CONFIG_PATH if config is None else config
                raise ValueError(
                    f"config does not contain [normal_shock]: {config_path}"
                )
            calculation = parse_normal_shock_config(config_data["normal_shock"])

        formatted = run_normal_shock(calculation)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    if calculation.output is None:
        typer.echo(formatted)
    else:
        calculation.output.write_text(formatted + "\n", encoding="utf-8")
        typer.echo(f"Written: {calculation.output}")


@normal_shock_app.command(name="init")
def cmd_init_normal_shock(
    output: Path = typer.Option(DEFAULT_CONFIG_PATH, "--output", "-o"),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """Write a focused normal-shock config file."""
    try:
        config_path = write_config(NORMAL_SHOCK_TEMPLATE, output, force=force)
    except FileExistsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Written: {config_path}")
    typer.echo(f"Then run: gasdyn normal-shock run --config {config_path}")
