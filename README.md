# gasdyn

Compressible inviscid flow calculator: shocks, expansions, isentropic relations. Python API, CLI, and web app.

[![Test](https://github.com/uahypersonics/gasdyn/actions/workflows/test.yml/badge.svg)](https://github.com/uahypersonics/gasdyn/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/gasdyn)](https://pypi.org/project/gasdyn/)
[![Docs](https://img.shields.io/badge/docs-Zensical-blue)](https://uahypersonics.github.io/gasdyn/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Install

```bash
pip install gasdyn
```

## Quick Start

```python
import gasdyn
```

Run a calculator directly through its solver group:

```bash
gasdyn isentropic run --mach 2.0
gasdyn taylor-maccoll run --mach 3.0 --cone-angle 10.0
```

Optionally create a complete dimensional cone-edge state from an upstream
FlowState while preserving the normal Taylor-Maccoll result:

```bash
pip install "gasdyn[flow-state]"
gasdyn taylor-maccoll run \
   --mach 3.0 \
   --cone-angle 10.0 \
   --output taylor_maccoll.json \
   --json \
   --upstream-state flow_state.json \
   --edge-state-output edge_state.json
```

Generate and run a config for one solver:

```bash
gasdyn taylor-maccoll init
gasdyn taylor-maccoll run
```

**Optional: enable Zsh tab completion**

Install gasdyn's completion script once, then open a new shell:

```zsh
gasdyn --install-completion zsh
```

You can then complete solver groups, commands, and options with Tab.

## Features

- **Isentropic relations**: pressure, temperature, density ratios
- **Normal shocks**: property jumps across shocks
- **Oblique shocks**: deflection angle, wave angle relations
- **Expansion fans**: Prandtl-Meyer function

## Documentation

Full documentation: https://uahypersonics.github.io/gasdyn

## Code Style

This project follows established Python community conventions so that
contributors can focus on the physics rather than inventing formatting rules.

| Convention | What it covers | Reference |
|---|---|---|
| [PEP 8](https://peps.python.org/pep-0008/) | Code formatting, naming, whitespace | Python standard style guide |
| [PEP 257](https://peps.python.org/pep-0257/) | Docstring structure (triple-quoted, imperative mood) | Python standard docstring conventions |
| [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) | Docstring sections (`Args`, `Returns`, `Raises`) | Google Python style guide |
| [Ruff](https://docs.astral.sh/ruff/) | Automated linting and formatting | Enforces PEP 8 compliance automatically |
| [typing / TYPE_CHECKING](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING) | Type hints for IDE support and static analysis | Python standard library |

## Versioning & Releasing

This project uses [Semantic Versioning](https://semver.org/) (`vMAJOR.MINOR.PATCH`):

- **MAJOR** (`v1.0.0`, `v2.0.0`): Breaking API changes
- **MINOR** (`v0.3.0`, `v0.4.0`): New features, backward-compatible
- **PATCH** (`v0.3.1`, `v0.3.2`): Bug fixes, minor corrections

To publish a new version to [PyPI](https://pypi.org/project/gasdyn/):

1. Commit and push to `main`
2. Tag and push:
   ```bash
   git tag -a vMAJOR.MINOR.PATCH -m "Release vMAJOR.MINOR.PATCH"
   git push origin vMAJOR.MINOR.PATCH
   ```

The GitHub Actions workflow will automatically build and publish to PyPI via Trusted Publishing.

## License

GNU General Public License v3.0 or later. See [LICENSE](LICENSE) for the
complete license terms.
