# django-click-uz — Django + Click.uz to‘liq integratsiya

Bu qo‘llanma **Django loyihangizdagi** kerakli fayllarni (`settings.py`, `models.py`, `views.py`, `urls.py`) bosqichma-bosqich bog‘lash uchun yozilgan.  
**Eslatma:** [GitHub click-pkg](https://github.com/PayTechUz/click-pkg) yoki videodagi `pip install click-pkg` — boshqa loyiha; bu yerda paket nomi **`django-click-uz`**, API esa tanish `click_up` importlari bilan mos keladi.

---

## 1. O‘rnatish (terminal)

```bash
pip install django-click-uz
```

---

## 2. `settings.py` — `INSTALLED_APPS` (muhim)

Videoda ba’zan faqat `'click_up'` yozilgan bo‘lishi mumkin. **Django migratsiyalari va admin `click_uz` ilovasida** — shuni qo‘shing. `click_up` — bu faqat **import qulayligi** (paket ichidagi modul), `INSTALLED_APPS` ro‘yxatiga emas.

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # ...
    "click_uz",  # majburiy: migratsiya, jadvallar, tarjimalar
    "order",     # o‘zingizning buyurtma ilovangiz
]
```

**Click konfiguratsiyasi** — ikkala usuldan biri (ikkala bo‘lsa, ustuvor **`CLICK` dict**):

**Variant A — bitta `CLICK` dict (tavsiya etiladi):**

```python
import os

CLICK = {
    "SERVICE_ID": int(os.environ["CLICK_SERVICE_ID"]),
    "MERCHANT_ID": int(os.environ["CLICK_MERCHANT_ID"]),
    "SECRET_KEY": os.environ["CLICK_SECRET_KEY"],
    # "USER_ID": 12345,  # ixtiyoriy; bo‘lmasa MERCHANT_ID Click API uchun ishlatiladi
    # Model orqali webhook (videodagi ORDER_MODEL o‘rniga):
    "ACCOUNT_MODEL": "order.Order",   # "order.models.Order" ham ishlaydi
    "AMOUNT_FIELD": "amount",
    "STATUS_FIELD": "status",
    # Status qiymatlari (modelingizdagi CharField qiymatlari bilan mos):
    "STATUS_PENDING": "pending",
    "STATUS_WAITING": "waiting_payment",  # prepare qabul qilingach
    "STATUS_PAID": "paid",
    "STATUS_CANCELLED": "cancelled",
    # Noyob transaction_param saqlasangiz (tavsiya):
    "MERCHANT_TRANS_FIELD": "transaction_param",
    "COMMISSION_PERCENT": 0,
    "DISABLE_ADMIN": False,
    "ENABLE_AUDIT": True,   # `ClickWebhookLog` jadvali; o‘chirish: False
    # Ishonchlilik (productionda proxy bilan `SECURE_PROXY_SSL_HEADER` ham):
    # "WEBHOOK_ALLOWED_CIDRS": ["203.0.113.0/24"],
}
```

**Variant B — videodagi kabi alohida o‘zgaruvchilar:**

```python
CLICK_SERVICE_ID = 12345
CLICK_MERCHANT_ID = 67890
CLICK_SECRET_KEY = "..."
CLICK_USER_ID = 1  # ixtiyoriy
CLICK_ACCOUNT_MODEL = "order.models.Order"
CLICK_AMOUNT_FIELD = "amount"
CLICK_STATUS_FIELD = "status"
CLICK_MERCHANT_TRANS_FIELD = "transaction_param"
CLICK_COMMISSION_PERCENT = 0
CLICK_DISABLE_ADMIN = False
```

Webhook ishlashi uchun **`HANDLER_CLASS`** yoki **`ACCOUNT_MODEL` + `AMOUNT_FIELD` + `STATUS_FIELD`** bo‘lishi kerak.

---

## 3. `models.py` — buyurtma (Order) namunasi

Paket `prepare` bosqichida statusni **`STATUS_WAITING`** (standart: `waiting_payment`) ga o‘zgartiradi, to‘lov tugagach **`paid`**, bekor **`cancelled`**. Shuning uchun modelda bu qiymatlar bo‘lishi yoki `CLICK` ichida `STATUS_*` ni o‘zingiznikiga moslang.

```python
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
    # Click `merchant_trans_id` bilan qidirish uchun (noyob param saqlanganda):
    transaction_param = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Order {self.pk} — {self.amount} UZS"
```

Keyin:

```bash
python manage.py makemigrations
python manage.py migrate
```

Bu `click_uz` jadvallarini ham yaratadi (`ENABLE_AUDIT=True` bo‘lsa audit jadvali ham).

---

## 4. `urls.py` — webhook yo‘li

**A) Paket tayyor URLlari** (tavsiya — bitta URL Click uchun):

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path("payment/click/", include("click_uz.urls")),
]
```

Endi webhook masalan: `https://sizning-domen.uz/payment/click/webhook/`  
(`prepare/`, `complete/`, `callback/` ham shu prefiks ostida.)

**B) Videodagi kabi o‘z view klassingiz** — shu yo‘lga ulang:

```python
from django.urls import path

from order.views import ClickWebhookAPIView  # misol

urlpatterns = [
    path("payment/click/update/", ClickWebhookAPIView.as_view(), name="click-webhook"),
]
```

Click kabinetida aynan shu **to‘liq HTTPS URL**ni ro‘yxatdan o‘tkazing.

---

## 5. `views.py` — webhook va to‘lov havolasi

### 5.1 Webhook (videodagi `ClickWebhook`)

`params` — bu lug‘at: buyurtma `id`, `merchant_trans_id`, `amount`, `state` va `payload` (Clickdan kelgan qisqa maydonlar).

```python
from click_up.views import ClickWebhook

from order.models import Order


class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        # params["payload"]["merchant_trans_id"] — Click yuborgan param
        merchant_trans_id = params["payload"].get("merchant_trans_id")
        order_id = params.get("id")
        try:
            order = Order.objects.get(pk=order_id)
            # statusni paket allaqachon "paid" qiladi; bu yerda signal, email va hokazo:
            ...
        except Order.DoesNotExist:
            pass

    def cancelled_payment(self, params):
        ...

    def prepare_accepted(self, params):
        """Prepare muvaffaqiyatli — ixtiyoriy"""
        ...
```

### 5.2 Buyurtma yaratish va pay havolasi

**Oddiy usul (video bilan yaqin):** har safar buyurtma `id` Clickga `transaction_param` sifatida ketadi (`unique_transaction_id=False`). Qidiruv `id` bo‘yicha — `MERCHANT_TRANS_FIELD` shart emas.

```python
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from click_up import ClickUp

from order.models import Order


@method_decorator(csrf_exempt, name="dispatch")
class CreateOrderView(View):
    def post(self, request):
        body = json.loads(request.body or "{}")
        amount = body.get("amount")
        order = Order.objects.create(user=request.user if request.user.is_authenticated else None, amount=amount)

        paylink = ClickUp().initializer.generate_pay_link(
            id=order.pk,
            amount=order.amount,
            return_url="https://example.com/order/done/",
            unique_transaction_id=False,
        )
        return JsonResponse({"order_id": order.pk, "payment_link": paylink})
```

**Tavsiya etilgan usul (noyob `transaction_param`):** takrorlanish va eski linklar bilan chalkashishni kamaytiradi. Avval paramni yaratib, modelga yozing, keyin **shu qator** bilan URL oching:

```python
from click_up import ClickUp, unique_transaction_param

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

Buning uchun `settings`da `MERCHANT_TRANS_FIELD = "transaction_param"` (yoki `CLICK` dictda `MERCHANT_TRANS_FIELD`) bo‘lishi kerak.

**REST Framework** ishlatsangiz, `APIView` ichidagi mantiq xuddi shu — faqat `request.data` dan o‘qing.

---

## 6. Videodagi boshqa maslahatlar — bu paket bilan

| Video / eski qo‘llanma | `django-click-uz` |
|------------------------|-------------------|
| `pip install click-pkg` | `pip install django-click-uz` |
| `INSTALLED_APPS`: `click_up` | Faqat **`click_uz`** |
| `is_test_mode=True` | Paketda alohida flag yo‘q; sinov uchun Click kabinetidagi test `SERVICE_ID` / hujjatdagi test URL (`CLICK["PAY_URL"]`) ishlating |
| `return_url` | To‘g‘ri — `generate_pay_link(..., return_url=...)` |
| Webhook orqali status | `ModelOrderHandler` statusni yangilaydi; qo‘shimcha logika — `successfully_payment` va hokazo |

---

## 7. Xavfsizlik (qisqa)

- **Imzo:** so‘rovlar `sign_string` bilan tekshiriladi — noto‘g‘ri yoki begona POSTlar rad etiladi.
- **HTTPS va IP:** `click_uz.webhook_guard` — productionda TLS, ixtiyoriy `WEBHOOK_ALLOWED_CIDRS`. Proxy orqali HTTPS bo‘lsa, Django’da `SECURE_PROXY_SSL_HEADER` ni sozlang.

---

Inglizcha qisqa README: [README.md](README.md)  
GitHub manbasi: [https://github.com/Matnazar-Matnazarov/django-click-uz](https://github.com/Matnazar-Matnazarov/django-click-uz)  
Click hujjatlari: [https://docs.click.uz/en/](https://docs.click.uz/en/)
