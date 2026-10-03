"""Tests for CLI using Typer's test runner."""

from pathlib import Path

import pytest
from click.utils import strip_ansi
from typer.testing import CliRunner

from gasdyn.cli.app import cli as app

runner = CliRunner()


def test_cli_help():
    """Test that CLI help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Gas dynamics" in result.stdout


def test_cli_no_args_shows_help():
    """Test that CLI shows help when invoked with no arguments."""
    # The main() function adds --help when no args, but we test the app directly
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Commands" in result.stdout


@pytest.mark.parametrize("command", ["init", "run"])
def test_cli_has_no_global_workflow_commands(command: str) -> None:
    """Root CLI exposes workflows only through solver groups."""
    result = runner.invoke(app, [command])

    assert result.exit_code == 2
    assert "No such command" in result.output


def test_cli_isentropic():
    """Test isentropic CLI command."""
    result = runner.invoke(app, ["isentropic", "run", "--mach", "2.0"])
    assert result.exit_code == 0
    assert "mach" in result.stdout
    assert "pres_ratio" in result.stdout


def test_cli_isentropic_area_ratio():
    """Test isentropic with area ratio."""
    result = runner.invoke(
        app,
        [
            "isentropic",
            "run",
            "--area-ratio",
            "1.6875",
            "--branch",
            "supersonic",
        ],
    )
    assert result.exit_code == 0
    assert "mach" in result.stdout


def test_cli_isentropic_error():
    """Test isentropic with invalid input."""
    result = runner.invoke(app, ["isentropic", "run", "--mach", "2.0", "--area-ratio", "1.5"])
    assert result.exit_code == 1
    # Error messages appear in output (Typer captures both stdout and stderr)
    assert "error" in result.output.lower() or "Must provide exactly one input" in str(
        result.exception
    )


def test_cli_normal_shock():
    """Test normal shock CLI command."""
    result = runner.invoke(app, ["normal-shock", "run", "--mach-1", "2.0"])
    assert result.exit_code == 0
    assert "mach" in result.stdout


def test_cli_normal_shock_from_pres_ratio():
    """Test normal shock from pressure ratio."""
    result = runner.invoke(app, ["normal-shock", "run", "--pres-ratio", "4.5"])
    assert result.exit_code == 0
    assert "mach_1" in result.stdout


def test_cli_normal_shock_error():
    """Test normal shock with invalid input."""
    result = runner.invoke(
        app,
        ["normal-shock", "run", "--mach-1", "2.0", "--pres-ratio", "4.5"],
    )
    assert result.exit_code == 1


def test_cli_oblique():
    """Test oblique shock CLI command."""
    result = runner.invoke(
        app,
        ["oblique", "run", "--mach", "2.0", "--deflection-angle", "10.0"],
    )
    assert result.exit_code == 0
    assert "shock_angle" in result.stdout


def test_cli_oblique_strong():
    """Test oblique shock with strong branch."""
    result = runner.invoke(
        app,
        [
            "oblique",
            "run",
            "--mach",
            "2.0",
            "--deflection-angle",
            "10.0",
            "--branch",
            "strong",
        ],
    )
    assert result.exit_code == 0
    assert "shock_angle" in result.stdout


def test_cli_oblique_error():
    """Test oblique with invalid input."""
    result = runner.invoke(app, ["oblique", "run", "--mach", "2.0"])
    assert result.exit_code == 1


def test_cli_prandtl_meyer():
    """Test Prandtl-Meyer CLI command."""
    result = runner.invoke(
        app,
        [
            "prandtl-meyer",
            "run",
            "--mach-1",
            "2.0",
            "--deflection-angle",
            "10.0",
        ],
    )
    assert result.exit_code == 0
    assert "mach_2" in result.stdout


def test_cli_prandtl_meyer_from_mach_numbers():
    """Test Prandtl-Meyer from two Mach numbers."""
    result = runner.invoke(
        app,
        ["prandtl-meyer", "run", "--mach-1", "2.0", "--mach-2", "3.0"],
    )
    assert result.exit_code == 0
    assert "deflection_angle" in result.stdout


def test_cli_prandtl_meyer_error():
    """Test Prandtl-Meyer with invalid input."""
    result = runner.invoke(app, ["prandtl-meyer", "run", "--mach-1", "2.0"])
    assert result.exit_code == 1


def test_cli_cone():
    """Test taylor-maccoll CLI command."""
    result = runner.invoke(
        app,
        ["taylor-maccoll", "run", "--mach", "3.0", "--cone-angle", "10.0"],
    )
    assert result.exit_code == 0
    assert "shock_angle" in result.stdout
    assert "mach_cone" in result.stdout


def test_cli_cone_error():
    """Test taylor-maccoll with invalid input."""
    result = runner.invoke(app, ["taylor-maccoll", "run", "--mach", "3.0"])
    assert result.exit_code == 1


def test_cli_cone_no_args_shows_help():
    """Test taylor-maccoll with no args shows subcommand help."""
    result = runner.invoke(app, ["taylor-maccoll"])
    output = strip_ansi(result.stdout)

    assert result.exit_code == 0
    assert "Taylor-Maccoll conical-flow calculations" in output
    assert "init" in output
    assert "run" in output


def test_cli_cone_init_and_run_config() -> None:
    """Taylor-Maccoll init writes a focused config consumed by run."""
    with runner.isolated_filesystem():
        init_result = runner.invoke(app, ["taylor-maccoll", "init"])
        run_result = runner.invoke(app, ["taylor-maccoll", "run"])

        assert init_result.exit_code == 0
        assert Path("gasdyn.toml").is_file()
        assert run_result.exit_code == 0
        assert Path("taylor_maccoll.json").is_file()


def test_cli_cone_writes_optional_edge_flow_state() -> None:
    """Taylor-Maccoll preserves its result and writes a canonical edge state."""
    flow_state = pytest.importorskip("flow_state")
    from flow_state.io import read_json, write_json

    with runner.isolated_filesystem():
        upstream_state = flow_state.solve(
            mach=3.0,
            pres=2500.0,
            temp=220.0,
        )
        write_json(upstream_state, "flow_state.json")

        result = runner.invoke(
            app,
            [
                "taylor-maccoll",
                "run",
                "--mach",
                "3.0",
                "--cone-angle",
                "10.0",
                "--json",
                "--output",
                "taylor_maccoll.json",
                "--upstream-state",
                "flow_state.json",
                "--edge-state-output",
                "edge_state.json",
            ],
        )

        edge_state = read_json("edge_state.json")

        assert result.exit_code == 0
        assert Path("taylor_maccoll.json").is_file()
        assert edge_state.mach == pytest.approx(2.7101238158301735)
        assert edge_state.pres > upstream_state.pres
        assert edge_state.temp > upstream_state.temp
        assert edge_state.transport_model == upstream_state.transport_model
        assert edge_state.provenance["builder"] == "gasdyn.taylor_maccoll"


def test_cli_cone_requires_both_edge_state_paths() -> None:
    """Edge-state output requires a complete upstream FlowState path."""
    result = runner.invoke(
        app,
        [
            "taylor-maccoll",
            "run",
            "--mach",
            "3.0",
            "--cone-angle",
            "10.0",
            "--edge-state-output",
            "edge_state.json",
        ],
    )

    assert result.exit_code == 1
    assert "must be provided together" in result.output


def test_cli_cone_config_writes_optional_edge_flow_state() -> None:
    """Configured Taylor-Maccoll runs can emit the secondary edge state."""
    flow_state = pytest.importorskip("flow_state")
    from flow_state.io import read_json, write_json

    config_text = """\
[taylor_maccoll]
mach = 3.0
cone_angle = 10.0
format = "json"
output = "taylor_maccoll.json"
upstream_state = "flow_state.json"
edge_state_output = "edge_state.json"
"""

    with runner.isolated_filesystem():
        upstream_state = flow_state.solve(
            mach=3.0,
            pres=2500.0,
            temp=220.0,
        )
        write_json(upstream_state, "flow_state.json")
        Path("gasdyn.toml").write_text(config_text, encoding="utf-8")

        result = runner.invoke(app, ["taylor-maccoll", "run"])
        edge_state = read_json("edge_state.json")

        assert result.exit_code == 0
        assert Path("taylor_maccoll.json").is_file()
        assert edge_state.mach == pytest.approx(2.7101238158301735)


def test_cli_json_output():
    """Test JSON output option."""
    result = runner.invoke(app, ["isentropic", "run", "--mach", "2.0", "--json"])
    assert result.exit_code == 0
    assert '"mach"' in result.stdout


def test_cli_json_output_oblique():
    """Test JSON output for oblique shock."""
    result = runner.invoke(
        app,
        [
            "oblique",
            "run",
            "--mach",
            "2.0",
            "--deflection-angle",
            "10.0",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert '"mach_1"' in result.stdout
    assert '"shock_angle"' in result.stdout


def test_cli_custom_gamma():
    """Test custom gamma value."""
    result = runner.invoke(
        app,
        ["isentropic", "run", "--mach", "2.0", "--gamma", "1.67"],
    )
    assert result.exit_code == 0
    assert "1.67" in result.stdout
