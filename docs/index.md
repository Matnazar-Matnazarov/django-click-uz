# django-click-uz

Production-oriented **Django 5+** integration for the [Click.uz](https://docs.click.uz/en/) merchant / Shop API: payment links, prepare/complete callbacks, signatures, optional audit logging, and deployment-oriented webhook checks.

## Features

- **`click_uz`** — Django app (models, URLs, views, translations).
- **`click_up`** — Familiar import paths (`ClickUp`, `ClickWebhook`) without a second `INSTALLED_APPS` entry.
- **Settings** — Single `CLICK` dict or flat `CLICK_*` variables.
- **Order models** — Optional `ModelOrderHandler` via `ACCOUNT_MODEL` + field names.

## Quick links

- [Installation](installation.md)
- [Configuration](configuration.md)
- [English README on GitHub](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/README.md)
- [O‘zbekcha qo‘llanma (README_UZ)](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/README_UZ.md)
- [Changelog](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/CHANGELOG.md)
- [Click official docs](https://docs.click.uz/en/)

## License

MIT — see the repository `LICENSE` file.
