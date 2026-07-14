# gasdyn

`gasdyn` is a Python package for inviscid compressible-flow relations and conical-flow calculations.

## Quick Start

### Install

```bash
pip install gasdyn
```

### Run

=== "CLI"

	```bash
	gasdyn oblique --mach 6.0 --deflection-angle 8.0
	```

=== "API"

	```python
	from gasdyn import solve_oblique

	result = solve_oblique(mach=6.0, deflection_angle=8.0)
	print(result.shock_angle)
	```

## Feedback & Contributing

Questions, bug reports, and contributions are welcome. If something unexpected
comes up while using this package, or there are ideas for improvement, opening
an issue or starting a discussion is the best first step.

Using a label when opening an issue helps prioritize and track requests:

- [Ask a question](https://github.com/uahypersonics/gasdyn/issues/new?labels=question)
- [Report a bug](https://github.com/uahypersonics/gasdyn/issues/new?labels=bug)
- [Suggest a feature](https://github.com/uahypersonics/gasdyn/issues/new?labels=enhancement)

For those interested in contributing code or documentation, the
[Contributing Guide](https://github.com/uahypersonics/gasdyn/blob/main/CONTRIBUTING.md)
covers how to set up a dev environment, run tests, and submit a PR.

## License

BSD-3-Clause. See [LICENSE](https://github.com/uahypersonics/gasdyn/blob/main/LICENSE)
for details.
