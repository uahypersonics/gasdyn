"""Read and write gasdyn TOML configuration files."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

# --------------------------------------------------
# default config path
# --------------------------------------------------
DEFAULT_CONFIG_PATH = Path("gasdyn.toml")


# --------------------------------------------------
# read config
# --------------------------------------------------
def read_config(path: str | Path | None = None) -> dict[str, Any]:
    """Read a gasdyn TOML configuration file.

    Args:
        path: Config path. Defaults to ``gasdyn.toml``.

    Returns:
        Parsed top-level TOML mapping.

    Raises:
        FileNotFoundError: If the config file does not exist.
        TypeError: If the TOML root is not a table.
    """

    # resolve config path
    config_path = DEFAULT_CONFIG_PATH if path is None else Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"config file not found: {config_path}")

    # read TOML data
    with config_path.open("rb") as file_obj:
        config = tomllib.load(file_obj)

    # validate the document root
    if not isinstance(config, dict):
        raise TypeError("gasdyn config root must be a TOML table")

    return config


# --------------------------------------------------
# write config
# --------------------------------------------------
def write_config(
    template: str,
    path: str | Path | None = None,
    *,
    force: bool = False,
) -> Path:
    """Write a gasdyn TOML template.

    Args:
        template: TOML template text.
        path: Output path. Defaults to ``gasdyn.toml``.
        force: Overwrite an existing file when true.

    Returns:
        Written config path.

    Raises:
        FileExistsError: If the output exists and ``force`` is false.
    """

    # resolve output path
    config_path = DEFAULT_CONFIG_PATH if path is None else Path(path)

    # protect existing user configuration
    if config_path.exists() and not force:
        raise FileExistsError(
            f"config file already exists: {config_path}; use --force to overwrite"
        )

    # write template
    config_path.write_text(template, encoding="utf-8")

    return config_path
