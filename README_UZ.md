# django-click-uz — Django + Click.uz integratsiyasi

[![CI](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml/badge.svg)](https://github.com/Matnazar-Matnazarov/django-click-uz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Python](https://img.shields.io/pypi/pyversions/django-click-uz.svg)](https://pypi.org/project/django-click-uz/)
[![Django](https://img.shields.io/badge/Django-5%2B-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Click.uz](https://img.shields.io/badge/To‘lov-Click.uz-00a651)](https://docs.click.uz/en/)

**Django 5+** uchun [Click.uz](https://docs.click.uz/en/) Shop API: to‘lov havolasi, prepare/complete webhooklar, MD5 imzo, ixtiyoriy audit, takrorlashdan himoya, production uchun HTTPS va ixtiyoriy IP filtri.

[Eski click-pkg / video](https://github.com/PayTechUz/click-pkg) bilan aralashtirmang: PyPI nomi **`django-click-uz`**, `click_up` esa faqat **import** uchun qulay modul.

| | |
|--|--|
| **English README** | [README.md](README.md) |
| **O‘zgarishlar jurnali** | [CHANGELOG.md](CHANGELOG.md) |
| **Manba kod** | [github.com/Matnazar-Matnazarov/django-click-uz](https://github.com/Matnazar-Matnazarov/django-click-uz) |
| **Qo‘shimcha `docs/`** | [repodagi `docs/`](https://github.com/Matnazar-Matnazarov/django-click-uz/tree/main/docs) |

---

## Paket tarkibi

| Qism | Vazifasi |
|------|----------|
| **`click_uz`** | Django ilovasi: `INSTALLED_APPS`, migratsiya, `urls`. Yo‘llar: `prepare/`, `complete/`, `callback/`, `webhook/`. `webhook_guard`, `ModelOrderHandler`, signalalar, `locale/uz`. |
| **`click_up`** | Faqat import: `ClickUp`, `ClickWebhook`, `unique_transaction_param`. **`INSTALLED_APPS`ga qo‘shmang.** |
| **Sozlama** | `CLICK` dict yoki tekis `CLICK_*`; ixtiyoriy `WEBHOOK_ALLOWED_CIDRS`, `WEBHOOK_REQUIRE_HTTPS`, `WEBHOOK_STRICT_IN_DEBUG`. |

---

## Talablar

- Python **3.12+**
- Django **5.0+**

---

## O‘rnatish

```bash
pip install django-click-uz
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "click_uz",  # majburiy
    "orders",    # buyurtma modeli turgan ilova
]
```

**Muhim:** videoda ba’zan `click_up` yoziladi — u **ilova emas**. Migratsiya va jadvallar faqat **`click_uz`** da.

---

## Sozlash (`CLICK`)

**Yagona qoida:** `CLICK` dict **va** tekis `CLICK_*` birga bo‘lsa, **ustuvor `CLICK`**.

### Variant A — `CLICK` dict (tavsiya)

```python
import os

CLICK = {
    "SERVICE_ID": int(os.environ["CLICK_SERVICE_ID"]),
    "MERCHANT_ID": int(os.environ["CLICK_MERCHANT_ID"]),
    "SECRET_KEY": os.environ["CLICK_SECRET_KEY"],
    # "USER_ID": 12345,  # ixtiyoriy; bo‘lmasa MERCHANT_ID ishlatiladi
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
    # Production (ixtiyoriy):
    # "WEBHOOK_ALLOWED_CIDRS": ["203.0.113.0/24"],
    # "WEBHOOK_STRICT_IN_DEBUG": True,
}
```

### Variant B — tekis o‘zgaruvchilar (video uslubi)

```python
CLICK_SERVICE_ID = 12345
CLICK_MERCHANT_ID = 67890
CLICK_SECRET_KEY = "maxfiy-kalit"
CLICK_ACCOUNT_MODEL = "orders.Order"
CLICK_AMOUNT_FIELD = "amount"
CLICK_STATUS_FIELD = "status"
CLICK_MERCHANT_TRANS_FIELD = "transaction_param"
CLICK_COMMISSION_PERCENT = 0
CLICK_DISABLE_ADMIN = False
```

Webhook uchun **`HANDLER_CLASS`** **yoki** **`ACCOUNT_MODEL` + `AMOUNT_FIELD` + `STATUS_FIELD`** kerak.

---

## Namuna: `Order` modeli

`prepare` dan keyin paket statusni odatda **`waiting_payment`** qiladi; to‘lov tugasa **`paid`**, rad etilsa **`cancelled`**. `CLICK` dagi `STATUS_*` qiymatlari model `choices` bilan mos kelishi kerak.

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
            ("pending", "Kutilmoqda"),
            ("waiting_payment", "To‘lov kutilmoqda"),
            ("paid", "To‘langan"),
            ("cancelled", "Bekor qilingan"),
        ],
        default="pending",
    )
    transaction_param = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Buyurtma {self.pk} — {self.amount} UZS"
```

```bash
python manage.py makemigrations
python manage.py migrate
```

`ENABLE_AUDIT=True` bo‘lsa, `click_uz` audit jadvali ham yaratiladi.

---

## `urls.py`

### A) Paket URLlarini ulash (tavsiya)

```python
from django.urls import include, path

urlpatterns = [
    path("payment/click/", include("click_uz.urls")),
]
```

Webhook misol: `https://sizning-domen.uz/payment/click/webhook/`

### B) O‘z view klassingiz (video kabi)

```python
from django.urls import path

from orders.views import ClickWebhookAPIView

urlpatterns = [
    path("payment/click/update/", ClickWebhookAPIView.as_view(), name="click-webhook"),
]
```

Click kabinetiga **to‘liq HTTPS** manzilni yozing.

---

## `views.py`: webhook + to‘lov havolasi

### Webhook

`params` ichida buyurtma maydonlari (`id`, `merchant_trans_id`, `amount`, `state`, …) va Clickdan kelgan qisqa ma’lumot `payload` ichida.

```python
# orders/views.py
from click_up.views import ClickWebhook

from .models import Order


class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        order_id = params.get("id")
        try:
            order = Order.objects.get(pk=order_id)
            # Paket statusni allaqachon "paid" qiladi; bu yerda email, log va hokazo
        except Order.DoesNotExist:
            pass

    def cancelled_payment(self, params):
        pass

    def prepare_accepted(self, params):
        """Ixtiyoriy: prepare muvaffaqiyatidan keyin."""
        pass
```

### Buyurtma yaratish + pay havolasi (oddiy — `id` = transaction_param)

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
            return_url="https://example.com/order/done/",
            unique_transaction_id=False,
        )
        return JsonResponse({"order_id": order.pk, "payment_link": paylink})
```

### Tavsiya: har checkout uchun noyob `transaction_param`

```python
from click_up import ClickUp, unique_transaction_param

from .models import Order

tid = unique_transaction_param(order.pk)
order.transaction_param = tid
order.save(update_fields=["transaction_param"])

paylink = ClickUp().initializer.generate_pay_link(
    id=order.pk,
    amount=order.amount,
    return_url="https://example.com/order/done/",
    transaction_param=tid,
)
```

Buning uchun `MERCHANT_TRANS_FIELD` / `CLICK_MERCHANT_TRANS_FIELD` = `"transaction_param"` bo‘lishi kerak.

**Django REST Framework:** xuddi shu mantiq `APIView` ichida, `request.data` orqali.

---

## Xavfsizlik

- Clickga qaytadigan JSON matnlari **inglizcha**; admin/config uchun `click_uz` tarjimalari (`locale/uz`).
- Asosiy himoya — **`sign_string`** bilan imzo tekshiruvi.
- **`webhook_guard`:** productionda HTTPS; ixtiyoriy **`WEBHOOK_ALLOWED_CIDRS`**. TLS proxy orqali ishlayotgan bo‘lsangiz, **`SECURE_PROXY_SSL_HEADER`** ni sozlang.

---

## Hujjatlar (lokal)

Internetda tayyor ReadTheDocs sayti yo‘q. MkDocs ni kompyuteringizda ko‘rish:

```bash
pip install -e ".[dev]"
# yoki: uv sync --all-extras
mkdocs serve
```

Terminaldagi manzilni oching (odatda `http://127.0.0.1:8000`).

---

## Rivojlantirish

```bash
pip install -e ".[dev]"
pytest
```

**Reliz:** `pyproject.toml` dagi `version`, `CHANGELOG.md`, commit, keyin **`vX.Y.Z`** tag va `git push origin vX.Y.Z` — [publish.yml](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/.github/workflows/publish.yml) PyPI ga yuklaydi. Har bir versiya PyPIda **bir marta** bo‘lishi kerak.

---

## Eski video / click-pkg bilan solishtirish

| Eski qo‘llanma | `django-click-uz` |
|----------------|-------------------|
| `pip install click-pkg` | `pip install django-click-uz` |
| `INSTALLED_APPS`: `click_up` | Faqat **`click_uz`** |
| `is_test_mode` | Alohida flag yo‘q; Click test `SERVICE_ID` / `PAY_URL` ishlating |
| `return_url` | `generate_pay_link(..., return_url=...)` |
| Webhook | `ModelOrderHandler` statusni yangilaydi; qo‘shimcha — `successfully_payment` va boshqalar |

---

## Litsenziya

MIT — repodagi [`LICENSE`](https://github.com/Matnazar-Matnazarov/django-click-uz/blob/main/LICENSE).

Rasmiy Click hujjatlari: [docs.click.uz](https://docs.click.uz/en/).
