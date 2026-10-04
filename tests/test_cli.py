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


def test_cli_help_lists_completion_options() -> None:
    """Test that shell-completion installation remains available."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "--install-completion" in result.stdout
    assert "--show-completion" in result.stdout


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


def test_cli_cone_run_uses_artifact_specific_options() -> None:
    """Taylor-Maccoll run exposes the dimensional state artifact options."""
    result = runner.invoke(app, ["taylor-maccoll", "run", "--help"])
    output = strip_ansi(result.stdout)

    assert result.exit_code == 0
    assert "--solution-output" in output
    assert "--pre-shock-state-input" in output
    assert "--post-shock-state-output" in output
    assert "--edge-state-output" in output
    assert "--json" not in output
    assert "--output" not in output
    assert "--freestream-state" not in output
    assert "--upstream-state" not in output


@pytest.mark.parametrize(
    "legacy_option",
    ["--json", "--output", "--freestream-state", "--upstream-state"],
)
def test_cli_cone_rejects_legacy_options(legacy_option: str) -> None:
    """Taylor-Maccoll run does not retain compatibility CLI options."""
    arguments = [
        "taylor-maccoll",
        "run",
        "--mach",
        "3.0",
        "--cone-angle",
        "10.0",
        legacy_option,
        "legacy.json",
    ]

    result = runner.invoke(app, arguments)

    assert result.exit_code != 0


def test_cli_cone_init_and_run_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Taylor-Maccoll init writes a focused config consumed by run."""
    monkeypatch.chdir(tmp_path)

    init_result = runner.invoke(app, ["taylor-maccoll", "init"])
    run_result = runner.invoke(app, ["taylor-maccoll", "run"])

    assert init_result.exit_code == 0
    assert Path("gasdyn.toml").is_file()
    assert run_result.exit_code == 0
    assert Path("taylor_maccoll.json").is_file()


def test_cli_cone_writes_optional_dimensional_flow_states(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Taylor-Maccoll writes canonical post-shock and cone-edge states."""
    flow_state = pytest.importorskip("flow_state")
    from flow_state.io import read_json, write_json

    monkeypatch.chdir(tmp_path)

    pre_shock_state = flow_state.solve(
        mach=3.0,
        pres=2500.0,
        temp=220.0,
    )
    write_json(pre_shock_state, "pre_shock_state.json")

    result = runner.invoke(
        app,
        [
            "taylor-maccoll",
            "run",
            "--mach",
            "3.0",
            "--cone-angle",
            "10.0",
            "--solution-output",
            "taylor_maccoll.json",
            "--pre-shock-state-input",
            "pre_shock_state.json",
            "--post-shock-state-output",
            "post_shock_state.json",
            "--edge-state-output",
            "edge_state.json",
        ],
    )

    post_shock_state = read_json("post_shock_state.json")
    edge_state = read_json("edge_state.json")

    assert result.exit_code == 0
    assert Path("taylor_maccoll.json").is_file()
    assert post_shock_state.pres > pre_shock_state.pres
    assert post_shock_state.temp > pre_shock_state.temp
    assert edge_state.mach == pytest.approx(2.7101238158301735)
    assert edge_state.pres > post_shock_state.pres
    assert edge_state.temp > post_shock_state.temp
    assert edge_state.transport_model == pre_shock_state.transport_model
    assert post_shock_state.provenance["state_location"] == "post_shock"
    assert edge_state.provenance["state_location"] == "edge"
    assert edge_state.provenance["builder"] == "gasdyn.taylor_maccoll"


@pytest.mark.parametrize(
    "state_output_option",
    ["--post-shock-state-output", "--edge-state-output"],
)
def test_cli_cone_state_output_requires_pre_shock_input(
    state_output_option: str,
) -> None:
    """Each dimensional state output requires a pre-shock FlowState input."""
    result = runner.invoke(
        app,
        [
            "taylor-maccoll",
            "run",
            "--mach",
            "3.0",
            "--cone-angle",
            "10.0",
            state_output_option,
            "state.json",
        ],
    )

    assert result.exit_code == 1
    assert "must be provided together" in result.output


def test_cli_cone_pre_shock_input_requires_state_output() -> None:
    """A pre-shock FlowState input must be consumed by a state output."""
    result = runner.invoke(
        app,
        [
            "taylor-maccoll",
            "run",
            "--mach",
            "3.0",
            "--cone-angle",
            "10.0",
            "--pre-shock-state-input",
            "pre_shock_state.json",
        ],
    )

    assert result.exit_code == 1
    assert "must be provided together" in result.output


@pytest.mark.parametrize(
    ("path_option", "invalid_path", "companion_options"),
    [
        ("--solution-output", "solution.txt", []),
        (
            "--pre-shock-state-input",
            "pre_shock_state.toml",
            ["--edge-state-output", "edge_state.json"],
        ),
        (
            "--post-shock-state-output",
            "post_shock_state.toml",
            ["--pre-shock-state-input", "pre_shock_state.json"],
        ),
        (
            "--edge-state-output",
            "edge_state.dat",
            ["--pre-shock-state-input", "pre_shock_state.json"],
        ),
    ],
)
def test_cli_cone_rejects_non_json_paths(
    path_option: str,
    invalid_path: str,
    companion_options: list[str],
) -> None:
    """Configured Taylor-Maccoll artifacts must use JSON filenames."""
    arguments = [
        "taylor-maccoll",
        "run",
        "--mach",
        "3.0",
        "--cone-angle",
        "10.0",
        path_option,
        invalid_path,
        *companion_options,
    ]

    result = runner.invoke(app, arguments)

    assert result.exit_code == 1
    assert "must use a .json file" in result.output


def test_cli_cone_config_writes_optional_dimensional_flow_states(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Configured Taylor-Maccoll runs can emit both dimensional states."""
    flow_state = pytest.importorskip("flow_state")
    from flow_state.io import read_json, write_json

    config_text = """\
[taylor_maccoll]
mach = 3.0
cone_angle = 10.0
solution_output = "taylor_maccoll.json"
pre_shock_state_input = "pre_shock_state.json"
post_shock_state_output = "post_shock_state.json"
edge_state_output = "edge_state.json"
"""

    monkeypatch.chdir(tmp_path)

    pre_shock_state = flow_state.solve(
        mach=3.0,
        pres=2500.0,
        temp=220.0,
    )
    write_json(pre_shock_state, "pre_shock_state.json")
    Path("gasdyn.toml").write_text(config_text, encoding="utf-8")

    result = runner.invoke(app, ["taylor-maccoll", "run"])
    post_shock_state = read_json("post_shock_state.json")
    edge_state = read_json("edge_state.json")

    assert result.exit_code == 0
    assert Path("taylor_maccoll.json").is_file()
    assert post_shock_state.pres > pre_shock_state.pres
    assert edge_state.mach == pytest.approx(2.7101238158301735)


@pytest.mark.parametrize(
    "legacy_field",
    ["output", "format", "freestream_state", "upstream_state"],
)
def test_cli_cone_rejects_legacy_config_fields(
    legacy_field: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Taylor-Maccoll config does not retain compatibility aliases."""
    config_text = f"""\
[taylor_maccoll]
mach = 3.0
cone_angle = 10.0
{legacy_field} = "legacy.json"
"""

    monkeypatch.chdir(tmp_path)
    Path("gasdyn.toml").write_text(config_text, encoding="utf-8")

    result = runner.invoke(app, ["taylor-maccoll", "run"])

    assert result.exit_code == 1
    assert f"unknown [taylor_maccoll] fields: {legacy_field}" in result.output


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
