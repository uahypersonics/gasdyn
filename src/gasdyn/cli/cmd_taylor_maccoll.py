"""CLI handler for ``gasdyn taylor-maccoll``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import typer

from gasdyn.config import (
    DEFAULT_CONFIG_PATH,
    TAYLOR_MACCOLL_TEMPLATE,
    TaylorMaccollConfig,
    parse_taylor_maccoll_config,
    read_config,
    write_config,
)
from gasdyn.runners import run_taylor_maccoll

# --------------------------------------------------
# Taylor-Maccoll command group
# --------------------------------------------------
taylor_maccoll_app = typer.Typer(
    name="taylor-maccoll",
    help="Taylor-Maccoll conical-flow calculations.",
    no_args_is_help=False,
    invoke_without_command=True,
)


@taylor_maccoll_app.callback()
def taylor_maccoll_callback(ctx: typer.Context) -> None:
    """Show Taylor-Maccoll help when no action is provided."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)


# --------------------------------------------------
# initialize Taylor-Maccoll config
# --------------------------------------------------
@taylor_maccoll_app.command(name="init")
def cmd_init_taylor_maccoll(
    output: Path = typer.Option(
        DEFAULT_CONFIG_PATH,
        "--output",
        "-o",
        help="Output config file.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite an existing config.",
    ),
) -> None:
    """Write a focused Taylor-Maccoll config file."""
    try:
        config_path = write_config(
            TAYLOR_MACCOLL_TEMPLATE,
            output,
            force=force,
        )
    except FileExistsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Written: {config_path}")
    typer.echo(f"Then run: gasdyn taylor-maccoll run --config {config_path}")


# --------------------------------------------------
# run Taylor-Maccoll from config or direct options
# --------------------------------------------------
@taylor_maccoll_app.command(name="run")
def cmd_run_taylor_maccoll(
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Config file. Defaults to gasdyn.toml.",
    ),
    mach: float | None = typer.Option(None, "--mach", help="Freestream Mach number"),
    cone_angle: float | None = typer.Option(
        None,
        "--cone-angle",
        help="Cone half-angle (degrees)",
    ),
    shock_angle: float | None = typer.Option(
        None,
        "--shock-angle",
        help="Shock wave angle (degrees)",
    ),
    gamma: float = typer.Option(1.4, "--gamma", help="Ratio of specific heats"),
    beta_guess: float | None = typer.Option(
        None,
        "--beta-guess",
        help="Initial shock-angle guess (degrees)",
    ),
    solution_output: Path | None = typer.Option(
        None,
        "--solution-output",
        "-o",
        help="Write the dimensionless solution to a JSON file.",
    ),
    pre_shock_state_input: Path | None = typer.Option(
        None,
        "--pre-shock-state-input",
        help="Canonical pre-shock FlowState JSON file.",
    ),
    post_shock_state_output: Path | None = typer.Option(
        None,
        "--post-shock-state-output",
        help="Write the canonical post-shock FlowState JSON file.",
    ),
    edge_state_output: Path | None = typer.Option(
        None,
        "--edge-state-output",
        help="Write the canonical cone-edge FlowState JSON file.",
    ),
) -> None:
    """Run a Taylor-Maccoll calculation."""

    # select direct-option mode when any primary solver input is provided
    direct_inputs = (mach, cone_angle, shock_angle)
    use_direct_options = any(value is not None for value in direct_inputs)

    try:
        if use_direct_options:
            if config is not None:
                raise ValueError("--config cannot be combined with direct solver inputs")

            calculation = TaylorMaccollConfig(
                mach=mach,
                cone_angle=cone_angle,
                shock_angle=shock_angle,
                gamma=gamma,
                beta_guess=beta_guess,
                solution_output=solution_output,
                pre_shock_state_input=pre_shock_state_input,
                post_shock_state_output=post_shock_state_output,
                edge_state_output=edge_state_output,
            )
        else:
            config_data = read_config(config)
            if "taylor_maccoll" not in config_data:
                config_path = DEFAULT_CONFIG_PATH if config is None else config
                raise ValueError(f"config does not contain [taylor_maccoll]: {config_path}")
            calculation = parse_taylor_maccoll_config(config_data["taylor_maccoll"])

        formatted = run_taylor_maccoll(calculation)
    except (ImportError, OSError, TypeError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from None

    # write configured output or print to the terminal
    if calculation.solution_output is None:
        typer.echo(formatted)
    else:
        calculation.solution_output.write_text(formatted + "\n", encoding="utf-8")
        typer.echo(f"Written: {calculation.solution_output}")

    # report the optional dimensional state artifacts separately
    if calculation.post_shock_state_output is not None:
        typer.echo(f"Written: {calculation.post_shock_state_output}")
    if calculation.edge_state_output is not None:
        typer.echo(f"Written: {calculation.edge_state_output}")
