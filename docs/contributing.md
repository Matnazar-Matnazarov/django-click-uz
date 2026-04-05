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
2. Create a GitHub **environment** named `pypi` only if your OIDC setup requires it (the default workflow does not).
3. Tag and push (use a **new** version each time; PyPI rejects duplicate file versions):

```bash
git tag -a v0.1.1 -m "Release 0.1.1"
git push origin v0.1.1
```

If the tag already exists locally, delete and recreate: `git tag -d v0.1.1` then tag again, or bump the version and use a new tag.

### Manual upload

```bash
uv run twine upload dist/*
```
