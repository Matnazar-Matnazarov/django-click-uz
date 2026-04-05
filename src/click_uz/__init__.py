"""Django integration for the Click.uz payment gateway."""

from __future__ import annotations

from decimal import Decimal

from click_uz.client import ClickMerchantClient
from click_uz.config import ClickMerchantConfig, merchant_config
from click_uz.services import PaymentService

__all__ = [
    "ClickClient",
    "ClickMerchantClient",
    "ClickMerchantConfig",
    "PaymentService",
    "get_merchant_config",
    "merchant_config",
]

__version__ = "0.1.0"

get_merchant_config = merchant_config


class ClickClient:
    def __init__(self, merchant: str = "default") -> None:
        self._merchant = merchant

    def create_payment(
        self,
        *,
        order_id: str,
        amount: Decimal | float | str,
        return_url: str | None = None,
        card_type: str | None = None,
        merchant_user_id: int | None = None,
    ) -> str:
        return PaymentService.create_payment_url(
            order_id=order_id,
            amount=amount,
            merchant=self._merchant,
            return_url=return_url,
            card_type=card_type,
            merchant_user_id=merchant_user_id,
        )

    def merchant_api(self) -> ClickMerchantClient:
        return PaymentService.merchant_client(self._merchant)
