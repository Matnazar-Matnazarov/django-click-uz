# Configuration

## `CLICK` dict (recommended)

```python
CLICK = {
    "SERVICE_ID": 12345,
    "MERCHANT_ID": 1,
    "SECRET_KEY": "your-secret",
    "ACCOUNT_MODEL": "orders.Order",
    "AMOUNT_FIELD": "amount",
    "STATUS_FIELD": "status",
}
```

Either **`HANDLER_CLASS`** or **`ACCOUNT_MODEL` + `AMOUNT_FIELD` + `STATUS_FIELD`** is required for webhooks.

## Flat settings (legacy style)

```python
CLICK_SERVICE_ID = 12345
CLICK_MERCHANT_ID = 1
CLICK_SECRET_KEY = "your-secret"
CLICK_ACCOUNT_MODEL = "orders.Order"
CLICK_AMOUNT_FIELD = "amount"
CLICK_STATUS_FIELD = "status"
```

If both `CLICK` and flat keys exist, **`CLICK` wins**.

## Webhook security (optional)

| Key | Purpose |
|-----|---------|
| `WEBHOOK_REQUIRE_HTTPS` | Force TLS (default: on when not in loose debug mode). |
| `WEBHOOK_STRICT_IN_DEBUG` | Enforce HTTPS even when `DEBUG=True`. |
| `WEBHOOK_ALLOWED_CIDRS` | Allow-list client IPs/CIDRs (empty = no IP filter). |

Behind a TLS-terminating proxy, set Django’s **`SECURE_PROXY_SSL_HEADER`**.

## Pay link

```python
from click_up import ClickUp

url = ClickUp().initializer.generate_pay_link(
    id=order.pk,
    amount=order.amount,
    return_url="https://example.com/done/",
)
```

Full integration steps: [README_UZ.md](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/README_UZ.md) (Uzbek) or [README.md](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/README.md) (English).
