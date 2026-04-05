"""Payment URL + Merchant API entry points."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from click_uz.client import ClickMerchantClient
from click_uz.config import merchant_config
from click_uz.exceptions import ClickUzConfigError
from click_uz.payment_url import build_payment_url

if TYPE_CHECKING:
    pass


class PaymentService:
    @staticmethod
    def create_payment_url(
        *,
        order_id: str,
        amount: Decimal | float | str,
        return_url: str | None = None,
        card_type: str | None = None,
        merchant_user_id: int | None = None,
        merchant: str = "default",
    ) -> str:
        if merchant != "default":
            raise ClickUzConfigError('Only merchant="default" is supported (single CLICK config).')
        cfg = merchant_config()
        dec = amount if isinstance(amount, Decimal) else Decimal(str(amount))
        return build_payment_url(
            cfg,
            transaction_param=str(order_id),
            amount=dec,
            return_url=return_url,
            card_type=card_type,
            merchant_user_id=merchant_user_id,
        )

    @staticmethod
    def merchant_client(merchant: str = "default") -> ClickMerchantClient:
        if merchant != "default":
            raise ClickUzConfigError('Only merchant="default" is supported (single CLICK config).')
        return ClickMerchantClient(merchant_config())
