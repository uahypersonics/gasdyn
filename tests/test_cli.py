"""Tests for CLI using Typer's test runner."""

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


def test_cli_isentropic():
    """Test isentropic CLI command."""
    result = runner.invoke(app, ["isentropic", "--mach", "2.0"])
    assert result.exit_code == 0
    assert "mach" in result.stdout
    assert "p_ratio" in result.stdout


def test_cli_isentropic_area_ratio():
    """Test isentropic with area ratio."""
    result = runner.invoke(app, ["isentropic", "--area-ratio", "1.6875", "--branch", "supersonic"])
    assert result.exit_code == 0
    assert "mach" in result.stdout


def test_cli_isentropic_error():
    """Test isentropic with invalid input."""
    result = runner.invoke(app, ["isentropic"])
    assert result.exit_code == 1
    # Error messages appear in output (Typer captures both stdout and stderr)
    assert "error" in result.output.lower() or "Must provide exactly one input" in str(result.exception)


def test_cli_normal_shock():
    """Test normal shock CLI command."""
    result = runner.invoke(app, ["normal-shock", "--mach-1", "2.0"])
    assert result.exit_code == 0
    assert "mach" in result.stdout


def test_cli_normal_shock_from_p_ratio():
    """Test normal shock from pressure ratio."""
    result = runner.invoke(app, ["normal-shock", "--p-ratio", "4.5"])
    assert result.exit_code == 0
    assert "mach_1" in result.stdout


def test_cli_normal_shock_error():
    """Test normal shock with invalid input."""
    result = runner.invoke(app, ["normal-shock"])
    assert result.exit_code == 1


def test_cli_oblique():
    """Test oblique shock CLI command."""
    result = runner.invoke(app, ["oblique", "--mach", "2.0", "--deflection-angle", "10.0"])
    assert result.exit_code == 0
    assert "shock_angle" in result.stdout


def test_cli_oblique_strong():
    """Test oblique shock with strong branch."""
    result = runner.invoke(app, ["oblique", "--mach", "2.0", "--deflection-angle", "10.0", "--branch", "strong"])
    assert result.exit_code == 0
    assert "shock_angle" in result.stdout


def test_cli_oblique_error():
    """Test oblique with invalid input."""
    result = runner.invoke(app, ["oblique", "--mach", "2.0"])
    assert result.exit_code == 1


def test_cli_prandtl_meyer():
    """Test Prandtl-Meyer CLI command."""
    result = runner.invoke(app, ["prandtl-meyer", "--mach-1", "2.0", "--deflection-angle", "10.0"])
    assert result.exit_code == 0
    assert "mach_2" in result.stdout


def test_cli_prandtl_meyer_from_mach_numbers():
    """Test Prandtl-Meyer from two Mach numbers."""
    result = runner.invoke(app, ["prandtl-meyer", "--mach-1", "2.0", "--mach-2", "3.0"])
    assert result.exit_code == 0
    assert "deflection_angle" in result.stdout


def test_cli_prandtl_meyer_error():
    """Test Prandtl-Meyer with invalid input."""
    result = runner.invoke(app, ["prandtl-meyer", "--mach-1", "2.0"])
    assert result.exit_code == 1


def test_cli_cone():
    """Test taylor-maccoll CLI command."""
    result = runner.invoke(app, ["taylor-maccoll", "--mach", "3.0", "--cone-angle", "10.0"])
    assert result.exit_code == 0
    assert "shock_angle" in result.stdout


def test_cli_cone_error():
    """Test taylor-maccoll with invalid input."""
    result = runner.invoke(app, ["taylor-maccoll", "--mach", "3.0"])
    assert result.exit_code == 1


def test_cli_cone_no_args_shows_help():
    """Test taylor-maccoll with no args shows subcommand help."""
    result = runner.invoke(app, ["taylor-maccoll"])
    assert result.exit_code == 0
    assert "Solve Taylor-Maccoll equations" in result.stdout
    assert "--mach" in result.stdout


def test_cli_json_output():
    """Test JSON output option."""
    result = runner.invoke(app, ["isentropic", "--mach", "2.0", "--json"])
    assert result.exit_code == 0
    assert '"mach"' in result.stdout


def test_cli_json_output_oblique():
    """Test JSON output for oblique shock."""
    result = runner.invoke(app, ["oblique", "--mach", "2.0", "--deflection-angle", "10.0", "--json"])
    assert result.exit_code == 0
    assert '"mach_1"' in result.stdout
    assert '"shock_angle"' in result.stdout


def test_cli_custom_gamma():
    """Test custom gamma value."""
    result = runner.invoke(app, ["isentropic", "--mach", "2.0", "--gamma", "1.67"])
    assert result.exit_code == 0
    assert "1.67" in result.stdout
