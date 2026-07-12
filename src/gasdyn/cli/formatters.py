"""Output formatters for CLI."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import dataclasses
import json

import typer


# --------------------------------------------------
# result printer
# --------------------------------------------------
def print_result(result, as_json: bool) -> None:
    """Print a gasdyn result to stdout as JSON or formatted text."""
    if as_json:
        typer.echo(_to_json(result))
    else:
        typer.echo(_to_str(result))


def _to_str(result) -> str:
    """Format a result dataclass as a human-readable table."""
    units = getattr(type(result), "_UNITS", {})
    fields = dataclasses.fields(result)

    # determine column width from the longest field name
    col_width = max(len(f.name) for f in fields)

    lines = ["=" * 60, "Gas Dynamics Results", "=" * 60]
    for f in fields:
        val  = getattr(result, f.name)
        unit = units.get(f.name, "-")
        lines.append(f"{f.name:<{col_width}}  :  {val:>14g}  [{unit}]")
    lines.append("=" * 60)

    return "\n".join(lines)


def _to_json(result) -> str:
    """Serialise a result dataclass to JSON with [value, unit] pairs."""
    units = getattr(type(result), "_UNITS", {})
    d = dataclasses.asdict(result)
    out = {k: [v, units.get(k, "-")] for k, v in d.items()}
    return json.dumps(out, indent=2)

