"""Build the Click payment redirect URL (`https://my.click.uz/services/pay`)."""

from __future__ import annotations

from decimal import Decimal
from urllib.parse import urlencode

from click_uz.config import ClickMerchantConfig


def format_amount(amount: Decimal) -> str:
    return f"{amount.quantize(Decimal('0.01')):.2f}"


def build_payment_url(
    cfg: ClickMerchantConfig,
    *,
    transaction_param: str,
    amount: Decimal,
    return_url: str | None = None,
    card_type: str | None = None,
    merchant_user_id: int | None = None,
) -> str:
    params: dict[str, str] = {
        "service_id": str(cfg.service_id),
        "merchant_id": str(cfg.merchant_id),
        "amount": format_amount(amount),
        "transaction_param": str(transaction_param),
    }
    uid = merchant_user_id if merchant_user_id is not None else cfg.merchant_user_id
    if uid is not None:
        params["merchant_user_id"] = str(uid)
    if return_url:
        params["return_url"] = return_url
    if card_type:
        params["card_type"] = card_type
    return f"{cfg.pay_base_url}?{urlencode(params)}"
