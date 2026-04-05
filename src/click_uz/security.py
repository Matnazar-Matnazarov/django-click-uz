"""Signature verification for Click Shop callbacks (prepare / complete).

Algorithm matches Click's reference PHP integration (`BasicPaymentsErrors::request_check`):
`md5(click_trans_id + service_id + secret_key + merchant_trans_id
     + (merchant_prepare_id if action==1 else '') + amount + action + sign_time)`
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Final

from click_uz.config import ClickMerchantConfig
from click_uz.types import ShopCallbackPayload

SIGNATURE_FAILED_ERROR: Final[int] = -1
INVALID_REQUEST_ERROR: Final[int] = -8


def build_shop_sign_string(payload: ShopCallbackPayload, secret_key: str) -> str:
    middle = str(payload.merchant_prepare_id) if payload.action == 1 else ""
    raw = (
        str(payload.click_trans_id)
        + str(payload.service_id)
        + secret_key
        + str(payload.merchant_trans_id)
        + middle
        + str(payload.amount)
        + str(payload.action)
        + str(payload.sign_time)
    )
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def verify_shop_signature(payload: ShopCallbackPayload, secret_key: str) -> bool:
    expected = build_shop_sign_string(payload, secret_key)
    got = payload.sign_string.strip().lower()
    if len(got) != len(expected):
        return False
    return hmac.compare_digest(expected, got)


def shop_payload_has_required_fields(payload: ShopCallbackPayload) -> bool:
    try:
        _ = payload.click_trans_id, payload.service_id, payload.merchant_trans_id
        _ = payload.amount, payload.action, payload.error, payload.error_note
        _ = payload.sign_time, payload.sign_string, payload.click_paydoc_id
        if payload.action == 1 and payload.merchant_prepare_id is None:
            return False
        return True
    except Exception:
        return False


def build_merchant_auth_header(cfg: ClickMerchantConfig, unix_ts: int | None = None) -> str:
    """`Auth: click_user_id:sha1(timestamp + secret_key):timestamp` (Merchant API)."""
    ts = int(time.time()) if unix_ts is None else int(unix_ts)
    digest = hashlib.sha1(f"{ts}{cfg.secret_key}".encode()).hexdigest()
    return f"{cfg.click_user_id}:{digest}:{ts}"
