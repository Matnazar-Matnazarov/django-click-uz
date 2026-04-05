# django-click-uz

[![CI](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml/badge.svg)](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Python](https://img.shields.io/pypi/pyversions/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Django](https://img.shields.io/badge/Django-5%2B-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Click.uz](https://img.shields.io/badge/Payment-Click.uz-00a651)](https://docs.click.uz/en/)

**Django 5+** integration for the [Click.uz](https://docs.click.uz/en/) Shop API: payment URLs, prepare/complete webhooks, MD5 signatures, optional audit log, replay protection, HTTPS and optional IP checks on callbacks.

| | |
|--|--|
| **O‘zbekcha (batafsil)** | [README_UZ.md](README_UZ.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |
| **Repository** | [github.com/Matnazar-Matnazarov/django-click-uz](https://github.com/Matnazar-Matnazarov/django-click-uz) |
| **Extra docs (Markdown)** | [`docs/`](https://github.com/Matnazar-Matnazarov/django-click-uz/tree/main/docs) |

---

## What’s in the package

| Part | Role |
|------|------|
| **`click_uz`** | Django app: add to `INSTALLED_APPS`, run migrations, include `urls`. Endpoints: `prepare/`, `complete/`, `callback/`, `webhook/`. Includes `webhook_guard`, `ModelOrderHandler`, signals, Uzbek `locale/uz`. |
| **`click_up`** | Compatibility imports only: `ClickUp`, `ClickWebhook`, `unique_transaction_param`. **Do not** add to `INSTALLED_APPS`. |
| **Config** | `CLICK` dict or flat `CLICK_*`; optional `WEBHOOK_ALLOWED_CIDRS`, `WEBHOOK_REQUIRE_HTTPS`, `WEBHOOK_STRICT_IN_DEBUG`. |

---

## Requirements

- Python **3.12+**
- Django **5.0+**

---

## Installation

```bash
pip install django-click-uz
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "click_uz",
    "orders",  # your app with Order model
]
```

---

## Configuration

Use **either** the `CLICK` dict **or** flat `CLICK_*` variables. If both are set, **`CLICK` wins**.

### Option A — `CLICK` dict (recommended)

```python
import os

CLICK = {
    "SERVICE_ID": int(os.environ["CLICK_SERVICE_ID"]),
    "MERCHANT_ID": int(os.environ["CLICK_MERCHANT_ID"]),
    "SECRET_KEY": os.environ["CLICK_SECRET_KEY"],
    # Optional Click user id for Merchant API; defaults to MERCHANT_ID if omitted
    # "USER_ID": 12345,
    "ACCOUNT_MODEL": "orders.Order",
    "AMOUNT_FIELD": "amount",
    "STATUS_FIELD": "status",
    "STATUS_PENDING": "pending",
    "STATUS_WAITING": "waiting_payment",
    "STATUS_PAID": "paid",
    "STATUS_CANCELLED": "cancelled",
    "MERCHANT_TRANS_FIELD": "transaction_param",
    "COMMISSION_PERCENT": 0,
    "DISABLE_ADMIN": False,
    "ENABLE_AUDIT": True,
    # Production hardening (optional):
    # "WEBHOOK_ALLOWED_CIDRS": ["203.0.113.0/24"],
    # "WEBHOOK_STRICT_IN_DEBUG": True,
}
```

### Option B — flat settings (legacy / click-pkg style)

```python
CLICK_SERVICE_ID = 12345
CLICK_MERCHANT_ID = 67890
CLICK_SECRET_KEY = "your-secret-key"
CLICK_ACCOUNT_MODEL = "orders.Order"
CLICK_AMOUNT_FIELD = "amount"
CLICK_STATUS_FIELD = "status"
CLICK_MERCHANT_TRANS_FIELD = "transaction_param"
CLICK_COMMISSION_PERCENT = 0
CLICK_DISABLE_ADMIN = False
```

Webhooks require **`HANDLER_CLASS`** **or** **`ACCOUNT_MODEL` + `AMOUNT_FIELD` + `STATUS_FIELD`**.

---

## Example: `Order` model

After **prepare**, the default handler sets status to `waiting_payment`; on success **complete** → `paid`; on rejection → `cancelled`. Align `STATUS_*` in `CLICK` with your `choices`.

```python
# orders/models.py
from django.conf import settings
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=32,
        choices=[
            ("pending", "Pending"),
            ("waiting_payment", "Waiting payment"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    transaction_param = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Order {self.pk} — {self.amount}"
```

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## URLs

**A) Include package routes** (single webhook URL for the Click cabinet):

```python
from django.urls import include, path

urlpatterns = [
    path("payment/click/", include("click_uz.urls")),
]
```

Webhook example: `https://your-domain.example/payment/click/webhook/`  
(same prefix: `prepare/`, `complete/`, `callback/`).

**B) Custom path with your `ClickWebhook` subclass:**

```python
from django.urls import path

from orders.views import ClickWebhookAPIView

urlpatterns = [
    path("payment/click/update/", ClickWebhookAPIView.as_view(), name="click-webhook"),
]
```

Register the **full HTTPS URL** in the Click merchant cabinet.

---

## Views: webhook + pay link

### Webhook subclass

`params` contains snapshot fields (`id`, `merchant_trans_id`, `amount`, `state`, …) and a nested `payload` with Click fields.

```python
# orders/views.py
from click_up.views import ClickWebhook

from .models import Order


class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        order_id = params.get("id")
        try:
            order = Order.objects.get(pk=order_id)
            # Model handler already set status to paid; add email, analytics, etc.
        except Order.DoesNotExist:
            pass

    def cancelled_payment(self, params):
        pass

    def prepare_accepted(self, params):
        """Optional: runs after prepare succeeds."""
        pass
```

### Create order + payment link (simple — order PK as `transaction_param`)

```python
import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from click_up import ClickUp

from .models import Order


@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderView(View):
    def post(self, request):
        body = json.loads(request.body or "{}")
        amount = body.get("amount")
        order = Order.objects.create(
            user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            amount=amount,
        )
        paylink = ClickUp().initializer.generate_pay_link(
            id=order.pk,
            amount=order.amount,
            return_url="https://example.com/orders/done/",
            unique_transaction_id=False,
        )
        return JsonResponse({"order_id": order.pk, "payment_link": paylink})
```

### Recommended: unique `transaction_param` per checkout

```python
from click_up import ClickUp, unique_transaction_param

from .models import Order

tid = unique_transaction_param(order.pk)
order.transaction_param = tid
order.save(update_fields=["transaction_param"])

paylink = ClickUp().initializer.generate_pay_link(
    id=order.pk,
    amount=order.amount,
    return_url="https://example.com/orders/done/",
    transaction_param=tid,
)
```

Requires `MERCHANT_TRANS_FIELD` / `CLICK_MERCHANT_TRANS_FIELD` pointing at `transaction_param` (see configuration above).

**Django REST Framework:** same logic inside `APIView.post`, using `request.data` instead of `json.loads`.

---

## Security & operations

- Callback **JSON** to Click stays in **English**; Django admin / config messages can use **`click_uz`** translations (`locale/uz/`).
- **MD5 `sign_string`** verification is the main authenticity check.
- **`click_uz.webhook_guard`**: enforce HTTPS in production; optional **`WEBHOOK_ALLOWED_CIDRS`**. Behind a TLS-terminating proxy, set **`SECURE_PROXY_SSL_HEADER`**.

---

## Documentation (local)

No hosted doc site is provided. To build the MkDocs site locally:

```bash
pip install -e ".[dev]"
# or: uv sync --all-extras
mkdocs serve
```

Open the URL printed in the terminal (usually `http://127.0.0.1:8000`).

---

## Development

```bash
pip install -e ".[dev]"
pytest
```

Releases: bump `version` in `pyproject.toml`, update `CHANGELOG.md`, commit, then tag and push **`vX.Y.Z`** (e.g. `v0.1.2`) to trigger [publish.yml](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/.github/workflows/publish.yml). Each PyPI upload needs a **new** version.

---

## vs older `click-pkg` tutorials

| Old tutorial | This package |
|--------------|--------------|
| `pip install click-pkg` | `pip install django-click-uz` |
| `INSTALLED_APPS`: `click_up` | Only **`click_uz`** |
| `is_test_mode` | Use Click test credentials / `PAY_URL` from Click docs if applicable |

---

## License

MIT — see [`LICENSE`](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/LICENSE).

Click API reference: [docs.click.uz](https://docs.click.uz/en/).
