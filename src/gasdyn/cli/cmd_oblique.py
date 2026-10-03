"""CLI handler for ``gasdyn oblique``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import typer

from gasdyn.config import (
    DEFAULT_CONFIG_PATH,
    OBLIQUE_TEMPLATE,
    ObliqueConfig,
    parse_oblique_config,
    read_config,
    write_config,
)
from gasdyn.runners import run_oblique

oblique_app = typer.Typer(
    name="oblique",
    help="Oblique-shock flow relations.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@oblique_app.callback()
def oblique_callback(ctx: typer.Context) -> None:
    """Show oblique-shock help when no action is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


# --------------------------------------------------
# oblique command
# --------------------------------------------------
@oblique_app.command(name="run")
def cmd_oblique(
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Config file. Defaults to gasdyn.toml."
    ),
    mach: float | None = typer.Option(None, "--mach", help="Upstream Mach number"),
    deflection_angle: float | None = typer.Option(None, "--deflection-angle", help="Flow deflection angle (degrees)"),
    shock_angle: float | None = typer.Option(None, "--shock-angle", help="Shock wave angle (degrees)"),
    branch: str = typer.Option("weak", "--branch", help="Shock branch (weak/strong)"),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write the result to a file."
    ),
) -> None:
    """Oblique shock relations."""
    direct_inputs = (mach, deflection_angle, shock_angle)
    use_direct_options = any(value is not None for value in direct_inputs)

    try:
        if use_direct_options:
            if config is not None:
                raise ValueError("--config cannot be combined with direct solver inputs")
            calculation = ObliqueConfig(
                mach=mach,
                deflection_angle=deflection_angle,
                shock_angle=shock_angle,
                branch=branch,
                gamma=gamma,
                output=output,
                output_format="json" if json else "text",
            )
        else:
            config_data = read_config(config)
            if "oblique" not in config_data:
                config_path = DEFAULT_CONFIG_PATH if config is None else config
                raise ValueError(f"config does not contain [oblique]: {config_path}")
            calculation = parse_oblique_config(config_data["oblique"])

        formatted = run_oblique(calculation)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    if calculation.output is None:
        typer.echo(formatted)
    else:
        calculation.output.write_text(formatted + "\n", encoding="utf-8")
        typer.echo(f"Written: {calculation.output}")


@oblique_app.command(name="init")
def cmd_init_oblique(
    output: Path = typer.Option(DEFAULT_CONFIG_PATH, "--output", "-o"),
    force: bool = typer.Option(False, "--force", "-f"),
) -> None:
    """Write a focused oblique-shock config file."""
    try:
        config_path = write_config(OBLIQUE_TEMPLATE, output, force=force)
    except FileExistsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Written: {config_path}")
    typer.echo(f"Then run: gasdyn oblique run --config {config_path}")
