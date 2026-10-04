"""Tests for generated gasdyn configuration templates."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import re
import tomllib

import pytest

from gasdyn.config import (
    ISENTROPIC_SECTION,
    NORMAL_SHOCK_SECTION,
    OBLIQUE_SECTION,
    PRANDTL_MEYER_SECTION,
    TAYLOR_MACCOLL_SECTION,
)

# --------------------------------------------------
# template registry
# --------------------------------------------------
TEMPLATE_SECTIONS = [
    ISENTROPIC_SECTION,
    NORMAL_SHOCK_SECTION,
    OBLIQUE_SECTION,
    PRANDTL_MEYER_SECTION,
    TAYLOR_MACCOLL_SECTION,
]


# --------------------------------------------------
# tests
# --------------------------------------------------
@pytest.mark.parametrize("section_text", TEMPLATE_SECTIONS)
def test_config_template_is_documented_and_valid(section_text: str) -> None:
    """Each generated setting should have above-line guidance in a titled block."""

    # validate that the uncommented defaults form valid TOML
    tomllib.loads(section_text)

    # require at least one titled block with an opening and closing separator
    separator = "# --------------------------------------------------"
    assert section_text.count(separator) >= 2

    # collect nonblank lines so comments remain immediately adjacent to settings
    lines = [line for line in section_text.splitlines() if line.strip()]
    assignment_pattern = re.compile(r"^(?:# )?[a-z][a-z0-9_]*\s*=")

    # check active and commented-out settings against their preceding info lines
    for index, line in enumerate(lines):
        if assignment_pattern.match(line) is None:
            continue

        info_line = lines[index - 1]
        assert info_line.startswith("# ")
        assert assignment_pattern.match(info_line) is None
