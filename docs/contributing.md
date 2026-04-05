# Contributing & releases

## Development

```bash
git clone https://github.com/Matnazar-Matnazarov/django-click-uz.git
cd django-click-uz
uv sync --all-extras
```

`uv.lock` is not committed; CI and local installs resolve dependencies from `pyproject.toml`.

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Or: `uv run python ruff_check.py` (check + format).

## Versioning

This project uses [Semantic Versioning](https://semver.org/): **MAJOR.MINOR.PATCH**.

- **MAJOR** — incompatible API changes.
- **MINOR** — backwards-compatible features.
- **PATCH** — backwards-compatible fixes.

Update **`version`** in `pyproject.toml` and add a dated section to **`CHANGELOG.md`** before tagging.

## Publishing to PyPI

### Build and check locally

```bash
uv sync --all-extras
uv build
uv run twine check dist/*
```

### GitHub Actions (recommended)

On push of a tag `v*`, the **Publish** workflow uploads wheels to PyPI.

1. Configure **Trusted publishing** on [pypi.org](https://pypi.org/) for project `django-click-uz` → your GitHub repo, or add a repository secret **`PYPI_API_TOKEN`** and adjust the workflow to use token auth if needed.
2. Create a GitHub **environment** named `pypi` if your OIDC setup requires it.
3. Tag and push:

```bash
git tag -s v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

### Manual upload

```bash
uv run twine upload dist/*
```
