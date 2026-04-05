# django-click-uz

[![CI](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml/badge.svg)](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Documentation](https://readthedocs.org/projects/django-click-uz/badge/?version=latest)](https://django-click-uz.readthedocs.io/en/latest/)

Django **5+** + [Click.uz](https://docs.click.uz/en/): pay links, webhooks, optional audit, replay protection, production-oriented guards.  
**Docs:** [django-click-uz.readthedocs.io](https://django-click-uz.readthedocs.io/en/latest/) · **Uzbek:** [README_UZ.md](README_UZ.md) · **Changelog:** [CHANGELOG.md](CHANGELOG.md) · **Source:** [github.com/Matnazar-Matnazarov/django-click-uz](https://github.com/Matnazar-Matnazarov/django-click-uz)

## Install

```bash
pip install django-click-uz
```

```python
INSTALLED_APPS = [
    # ...
    "click_uz",  # required: migrations & models live here (not "click_up")
]
```

`click_up` is only an **import alias** (familiar API); do **not** add it to `INSTALLED_APPS`.

---

## Settings

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

**Option B — flat `CLICK_*` names (legacy click-pkg style):**

```python
CLICK_SERVICE_ID = 12345
CLICK_MERCHANT_ID = 1
CLICK_SECRET_KEY = "secret"
CLICK_ACCOUNT_MODEL = "order.models.Order"
CLICK_AMOUNT_FIELD = "amount"
CLICK_STATUS_FIELD = "status"
```

If both exist, the **`CLICK`** dict wins. Webhooks need **`HANDLER_CLASS`** **or** **`ACCOUNT_MODEL` + `AMOUNT_FIELD` + `STATUS_FIELD`**.

---

## Full integration (files in your project)

This mirrors common **click-pkg / video** tutorials but uses this package’s real rules.

1. **`settings.py`** — `INSTALLED_APPS` includes **`click_uz`**; configure `CLICK` or flat keys as above.
2. **`models.py`** — e.g. an `Order` with `amount`, `status` (`pending` → `waiting_payment` after prepare → `paid` / `cancelled`), and optional `transaction_param` if you use **`MERCHANT_TRANS_FIELD`**.
3. **`urls.py`** — either include packaged routes:

   ```python
   path("payment/click/", include("click_uz.urls")),
   ```

   Webhook URL for the Click cabinet: `…/payment/click/webhook/`, **or** mount your own subclass on any path (e.g. `payment/click/update/`).

4. **`views.py`** — subclass `ClickWebhook` and override `successfully_payment`, `cancelled_payment`, optional `prepare_accepted`. `params` is a dict with snapshot fields plus `payload` (Click fields).

5. **Pay link** — `ClickUp().initializer.generate_pay_link(...)`.  
   - Video-style stable id: `unique_transaction_id=False` (uses order pk as `transaction_param`).  
   - Recommended: save a unique string to the order, then pass **`transaction_param=that_string`** (and set **`MERCHANT_TRANS_FIELD`**).  
   - Default: random suffix per call (`unique_transaction_id=True`); persist the value yourself if you use DB lookup by `merchant_trans_id`.

```python
from click_up import ClickUp, unique_transaction_param

tid = unique_transaction_param(order.pk)
order.transaction_param = tid
order.save(update_fields=["transaction_param"])
url = ClickUp().initializer.generate_pay_link(
    id=order.pk,
    amount=order.amount,
    return_url="https://example.com/done/",
    transaction_param=tid,
)
```

6. **Migrate:** `python manage.py migrate`

**vs older `click-pkg` videos:** package name is **`django-click-uz`**; **`click_up` is not a Django app**. There is no `is_test_mode` flag here—use Click’s test merchant/service or `PAY_URL` from docs if applicable.

---

## URLs (included routes)

```python
from django.urls import path
from click_up.views import ClickWebhook

class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        ...

urlpatterns = [
    path("payment/click/update/", ClickWebhookAPIView.as_view()),
]
```

Or use `click_uz.urls`: `prepare/`, `complete/`, `callback/`, `webhook/`.

---

## Security & ops

- Responses to Click stay **English**; admin/config strings can use **`click_uz` locale** (`locale/uz/`).
- **Signature** verification on webhook bodies is the main authenticity check.
- **HTTPS + optional IP allowlist:** see `click_uz.webhook_guard` and `CLICK["WEBHOOK_*"]` keys; behind TLS-terminating proxy set **`SECURE_PROXY_SSL_HEADER`**.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Docs: [https://docs.click.uz/en/](https://docs.click.uz/en/)
