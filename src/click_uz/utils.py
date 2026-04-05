"""Helpers for safe payment flows."""

from __future__ import annotations

import secrets
from dataclasses import asdict
from typing import Any

from click_uz.handlers import ClickOrderSnapshot
from click_uz.types import ShopCallbackPayload


def unique_transaction_param(public_id: str | int, *, entropy_bytes: int = 8) -> str:
    """
    Build a non-repeating ``transaction_param`` for each checkout (recommended).

    Format: ``"{public_id}-{hex}"`` — keeps the public id for debugging while the
    suffix makes collisions and blind retries across sessions practically impossible.
    """
    suffix = secrets.token_hex(entropy_bytes)
    return f"{public_id}-{suffix}"


def payment_params_dict(
    snapshot: ClickOrderSnapshot, payload: ShopCallbackPayload
) -> dict[str, Any]:
    """Dict for webhook user hooks (snapshot + subset of Click payload)."""
    d = asdict(snapshot)
    d["payload"] = {
        "click_trans_id": payload.click_trans_id,
        "merchant_trans_id": payload.merchant_trans_id,
        "amount": payload.amount,
        "action": payload.action,
        "error": payload.error,
        "error_note": payload.error_note,
        "sign_time": payload.sign_time,
    }
    return d
