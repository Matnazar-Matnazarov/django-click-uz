"""
click-pkg–style API (django-click-uz).

**INSTALLED_APPS:** use ``\"click_uz\"`` (migrations and admin live there).
Imports may use ``click_up`` for familiarity.
"""

from __future__ import annotations

from decimal import Decimal

from click_up.views import ClickWebhook
from click_uz.config import merchant_config
from click_uz.exceptions import ClickUzConfigError
from click_uz.services import PaymentService
from click_uz.utils import payment_params_dict, unique_transaction_param


class ClickUpInitializer:
    __slots__ = ("_parent",)

    def __init__(self, parent: ClickUp) -> None:
        self._parent = parent

    def generate_pay_link(
        self,
        *,
        id: int | str,
        amount: Decimal | float | str,
        return_url: str | None = None,
        unique_transaction_id: bool = True,
        transaction_param: str | None = None,
        **kwargs,
    ) -> str:
        if transaction_param is not None:
            tid = str(transaction_param)
        elif unique_transaction_id:
            tid = unique_transaction_param(id)
        else:
            tid = str(id)
        dec = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        return PaymentService.create_payment_url(
            order_id=tid,
            amount=dec,
            return_url=return_url,
            **kwargs,
        )


class ClickUp:
    __slots__ = ("initializer",)

    def __init__(
        self,
        service_id: str | int | None = None,
        merchant_id: str | int | None = None,
        secret_key: str | None = None,
    ) -> None:
        cfg = merchant_config()
        if service_id is not None and int(service_id) != cfg.service_id:
            raise ClickUzConfigError("service_id does not match Django settings.")
        if merchant_id is not None and int(merchant_id) != cfg.merchant_id:
            raise ClickUzConfigError("merchant_id does not match Django settings.")
        if secret_key is not None and str(secret_key) != cfg.secret_key:
            raise ClickUzConfigError("secret_key does not match Django settings.")
        self.initializer = ClickUpInitializer(self)


__all__ = [
    "ClickUp",
    "ClickUpInitializer",
    "ClickWebhook",
    "payment_params_dict",
    "unique_transaction_param",
]
