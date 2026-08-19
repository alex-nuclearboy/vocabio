# Vocabio documentation

The Vocabio project documentation is maintained with Sphinx.

The documentation covers project setup, local development, configuration,
development tooling, continuous integration, production deployment,
database operations, project structure, and technical reference material.
Application-specific documentation will be added as the project grows.

## Documentation source

The Sphinx source files are located in [`source/`](source/).

The main documentation index is
[`source/index.rst`](source/index.rst).

## Building the documentation

The commands below assume that the project development environment has
already been installed.

From the `docs` directory, build the HTML documentation with:

### Windows

```text
poetry run sphinx-build -M html source _build
```

### Linux and macOS

```text
poetry run sphinx-build -M html source _build
```

Alternatively, when the Poetry environment is already active, use the
provided Sphinx build wrappers:

### Windows

```text
make.bat html
```

### Linux and macOS

```text
make html
```

Generated files are written to `docs/_build/` and are not part of the
documentation source.

## Strict documentation validation

From the repository root, run the same strict Sphinx validation used by the
project checks:

```text
poetry run sphinx-build -E -a -W -n -T -b html docs/source docs/_build/html
```

The command treats warnings and unresolved references as build failures.
