"""Typed structures for Click Shop (prepare/complete) payloads."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class ShopCallbackPayload:
    """Raw fields Click sends for prepare (action=0) or complete (action=1)."""

    click_trans_id: str
    service_id: int
    click_paydoc_id: str
    merchant_trans_id: str
    amount: str
    action: int
    error: int
    error_note: str
    sign_time: str
    sign_string: str
    merchant_prepare_id: int | None

    @classmethod
    def from_request_mapping(cls, data: Mapping[str, Any]) -> ShopCallbackPayload:
        def req_str(key: str) -> str:
            v = data.get(key)
            if v is None:
                raise ValueError(f"missing {key}")
            return str(v).strip()

        def req_int(key: str) -> int:
            v = data.get(key)
            if v is None or v == "":
                raise ValueError(f"missing {key}")
            return int(v)

        action = req_int("action")
        merchant_prepare_id: int | None
        if action == 1:
            merchant_prepare_id = req_int("merchant_prepare_id")
        else:
            mp = data.get("merchant_prepare_id")
            merchant_prepare_id = int(mp) if mp not in (None, "") else None

        return cls(
            click_trans_id=req_str("click_trans_id"),
            service_id=req_int("service_id"),
            click_paydoc_id=req_str("click_paydoc_id"),
            merchant_trans_id=req_str("merchant_trans_id"),
            amount=req_str("amount"),
            action=action,
            error=req_int("error"),
            error_note=req_str("error_note"),
            sign_time=req_str("sign_time"),
            sign_string=req_str("sign_string"),
            merchant_prepare_id=merchant_prepare_id,
        )


@dataclass(slots=True)
class ShopPrepareResult:
    click_trans_id: str
    merchant_trans_id: str
    merchant_prepare_id: int
    merchant_confirm_id: int
    error: int
    error_note: str


@dataclass(slots=True)
class ShopCompleteResult:
    click_trans_id: str
    merchant_trans_id: str
    merchant_prepare_id: int
    merchant_confirm_id: int
    error: int
    error_note: str


def amount_to_decimal(amount: str) -> Decimal:
    return Decimal(amount)
