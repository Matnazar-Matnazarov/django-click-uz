# django-click-uz

[![CI](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml/badge.svg)](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Python](https://img.shields.io/pypi/pyversions/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Django](https://img.shields.io/badge/Django-5%2B-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Click.uz](https://img.shields.io/badge/Payment-Click.uz-00a651)](https://docs.click.uz/en/)

**Production-oriented Django 5+** integration for the [Click.uz](https://docs.click.uz/en/) Shop API: payment URLs, prepare/complete webhooks, MD5 signatures, optional audit log, replay protection, HTTPS / IP checks for callbacks.

| | |
|--|--|
| **Uzbek (full tutorial)** | [README_UZ.md](README_UZ.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |
| **Repository** | [github.com/Matnazar-Matnazarov/django-click-uz](https://github.com/Matnazar-Matnazarov/django-click-uz) |
| **Extra Markdown docs** | [`docs/`](https://github.com/Matnazar-Matnazarov/django-click-uz/tree/main/docs) (MkDocs sources) |

---

## What’s in the package

| Part | Role |
|------|------|
| **`click_uz`** | Django app: `INSTALLED_APPS`, migrations, `urls`, views (`prepare` / `complete` / `callback` / `webhook`), `webhook_guard`, `ModelOrderHandler`, signals, Uzbek `locale/uz`. |
| **`click_up`** | Same codebase, **import-only** compatibility (`ClickUp`, `ClickWebhook`, `generate_pay_link` style). **Not** an `INSTALLED_APPS` entry. |
| **Config** | `CLICK` dict or flat `CLICK_*` settings; optional `WEBHOOK_ALLOWED_CIDRS`, `WEBHOOK_REQUIRE_HTTPS`, etc. |
| **Tests / dev** | `pytest`, `ruff`, `mkdocs` (optional local doc site). |

---

## Requirements

- Python **3.12+**
- Django **5.0+**

---

## Install

```bash
pip install django-click-uz
```

```python
INSTALLED_APPS = [
    # ...
    "click_uz",
]
```

---

## Configuration (summary)

**Option A — `CLICK` dict (recommended):**

```python
CLICK = {
    "SERVICE_ID": os.getenv("CLICK_SERVICE_ID"),
    "MERCHANT_ID": os.getenv("CLICK_MERCHANT_ID"),
    "SECRET_KEY": os.getenv("CLICK_SECRET_KEY"),
    "ACCOUNT_MODEL": "order.Order",
    "AMOUNT_FIELD": "amount",
    "STATUS_FIELD": "status",
    "STATUS_WAITING": "waiting_payment",
    "MERCHANT_TRANS_FIELD": "transaction_param",
    "COMMISSION_PERCENT": 0,
    "DISABLE_ADMIN": False,
}
```

**Option B — flat `CLICK_*`** (legacy click-pkg style): see [Configuration](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/docs/configuration.md) in `docs/`.

Webhooks need **`HANDLER_CLASS`** **or** **`ACCOUNT_MODEL` + `AMOUNT_FIELD` + `STATUS_FIELD`**. If both dict and flat keys exist, **`CLICK` wins**.

---

## Integration checklist

1. **`settings.py`** — `click_uz` in `INSTALLED_APPS`; set `CLICK` or `CLICK_*`.
2. **`models.py`** — order model with `amount`, `status`, optional `transaction_param`.
3. **`urls.py`** — e.g. `path("payment/click/", include("click_uz.urls"))` → webhook at `…/payment/click/webhook/`, or mount your own `ClickWebhook` subclass.
4. **`views.py`** — override `successfully_payment`, `cancelled_payment`, optional `prepare_accepted`.
5. **Pay link** — `ClickUp().initializer.generate_pay_link(...)`; see [README_UZ.md](README_UZ.md) for stable vs unique `transaction_param`.
6. **Migrate** — `python manage.py migrate`.

Compared to older **click-pkg** tutorials: PyPI name is **`django-click-uz`**; only **`click_uz`** goes in `INSTALLED_APPS`.

---

## Documentation (local)

There is **no** hosted ReadTheDocs site for this repo. To browse the MkDocs site **locally**:

```bash
uv sync --all-extras   # or: pip install -e ".[dev]"
mkdocs serve
```

Then open the URL shown in the terminal (usually `http://127.0.0.1:8000`). Sources live under [`docs/`](https://github.com/Matnazar-Matnazarov/django-click-uz/tree/main/docs).

---

## Security & operations

- Click JSON responses use **English**; admin/config strings can use **`click_uz`** translations (`locale/uz/`).
- **Signature** checks on webhook payloads are the main authenticity control.
- **HTTPS + optional IP allowlist:** `click_uz.webhook_guard` and `CLICK["WEBHOOK_*"]`; behind TLS termination set **`SECURE_PROXY_SSL_HEADER`**.

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

Release workflow: bump `version` in `pyproject.toml`, update `CHANGELOG.md`, commit, then tag **`vX.Y.Z`** (e.g. `v0.1.1`) and `git push origin vX.Y.Z` — see [`.github/workflows/publish.yml`](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/.github/workflows/publish.yml). If a tag already exists, use the **next** version number.

---

## License

MIT — see [`LICENSE`](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/LICENSE).

Official Click API reference: [docs.click.uz](https://docs.click.uz/en/).
