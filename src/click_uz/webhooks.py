"""Shop prepare / complete — validate, retries, one DB transaction, audit."""

from __future__ import annotations

import hashlib
import logging
from decimal import Decimal
from typing import Any

from django.core.cache import cache
from django.db import transaction

from click_uz.config import audit_enabled, merchant_config, replay_enabled, replay_ttl
from click_uz.constants import ClickJson
from click_uz.handlers import BaseClickShopHandler, ClickOrderSnapshot, ClickOrderState
from click_uz.security import SIGNATURE_FAILED_ERROR, verify_shop_signature
from click_uz.types import ShopCallbackPayload, amount_to_decimal

logger = logging.getLogger(__name__)


def _digest(payload: ShopCallbackPayload) -> str:
    s = f"{payload.click_trans_id}|{payload.action}|{payload.merchant_trans_id}|{payload.amount}|{payload.sign_time}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _replay_hit(tid: str, action: int) -> bool:
    if not replay_enabled():
        return False
    return not cache.add(f"click_uz:{tid}:{action}", "1", timeout=replay_ttl())


def _audit(payload: ShopCallbackPayload, result: dict[str, Any], dg: str) -> None:
    if not audit_enabled():
        return
    try:
        from click_uz.models import ClickWebhookLog

        ClickWebhookLog.objects.create(
            click_trans_id=str(payload.click_trans_id)[:64],
            action=int(payload.action),
            merchant_trans_id=str(payload.merchant_trans_id)[:255],
            service_id=int(payload.service_id),
            error_code=int(result["error"]),
            request_digest=dg[:64],
        )
    except Exception:
        logger.exception("click_uz audit log failed")


def _bad_sig(payload: ShopCallbackPayload) -> dict[str, Any] | None:
    cfg = merchant_config()
    if int(cfg.service_id) != int(payload.service_id):
        return {"error": -8, "error_note": ClickJson.BAD_REQUEST}
    if not verify_shop_signature(payload, cfg.secret_key):
        return {"error": SIGNATURE_FAILED_ERROR, "error_note": ClickJson.SIGN_FAILED}
    return None


def _ok_prepare(payload: ShopCallbackPayload, mid: int) -> dict[str, Any]:
    mid = int(mid)
    return {
        "click_trans_id": payload.click_trans_id,
        "merchant_trans_id": payload.merchant_trans_id,
        "merchant_confirm_id": mid,
        "merchant_prepare_id": mid,
        "error": 0,
        "error_note": ClickJson.SUCCESS,
    }


def _complete_result(
    payload: ShopCallbackPayload,
    inner: dict[str, Any],
    handler: BaseClickShopHandler,
    order: ClickOrderSnapshot,
) -> dict[str, Any]:
    ce, ie = int(payload.error), int(inner["error"])
    if ce < 0 and ie not in (-4, -9):
        handler.on_complete_reject(order, payload)
        return {
            "click_trans_id": payload.click_trans_id,
            "merchant_trans_id": payload.merchant_trans_id,
            "merchant_confirm_id": order.id,
            "merchant_prepare_id": order.id,
            "error": -9,
            "error_note": ClickJson.CANCELLED,
        }
    if ie == 0:
        handler.on_complete_success(order, payload)
    return {
        "click_trans_id": payload.click_trans_id,
        "merchant_trans_id": payload.merchant_trans_id,
        "merchant_confirm_id": order.id,
        "merchant_prepare_id": order.id,
        "error": inner["error"],
        "error_note": inner["error_note"],
    }


def process_shop_prepare(
    payload: ShopCallbackPayload, handler: BaseClickShopHandler
) -> dict[str, Any]:
    dg = _digest(payload)
    if payload.action != 0:
        r = {"error": -3, "error_note": ClickJson.ACTION_NOT_FOUND}
        _audit(payload, r, dg)
        return r
    if _replay_hit(payload.click_trans_id, payload.action):
        r = {"error": -8, "error_note": ClickJson.DUPLICATE}
        _audit(payload, r, dg)
        return r
    bad = _bad_sig(payload)
    if bad:
        _audit(payload, bad, dg)
        return bad

    order = handler.get_order_by_merchant_trans_id(payload.merchant_trans_id)
    if order is None:
        r = {"error": -5, "error_note": ClickJson.NO_USER}
        _audit(payload, r, dg)
        return r
    if order.state == ClickOrderState.PAID:
        r = {"error": -4, "error_note": ClickJson.PAID}
        _audit(payload, r, dg)
        return r
    if order.state == ClickOrderState.CANCELLED:
        r = {"error": -9, "error_note": ClickJson.CANCELLED}
        _audit(payload, r, dg)
        return r

    try:
        req = amount_to_decimal(payload.amount)
    except Exception:
        r = {"error": -2, "error_note": ClickJson.BAD_AMOUNT}
        _audit(payload, r, dg)
        return r
    if abs(order.amount - req) > Decimal("0.01"):
        r = {"error": -2, "error_note": ClickJson.BAD_AMOUNT}
        _audit(payload, r, dg)
        return r

    if order.state == ClickOrderState.WAITING:
        r = _ok_prepare(payload, order.id)
        _audit(payload, r, dg)
        return r

    with transaction.atomic():
        mid = int(handler.on_prepare_success(order, payload))
        r = _ok_prepare(payload, mid)
        _audit(payload, r, dg)
    return r


def process_shop_complete(
    payload: ShopCallbackPayload, handler: BaseClickShopHandler
) -> dict[str, Any]:
    dg = _digest(payload)
    if payload.action != 1:
        r = {"error": -3, "error_note": ClickJson.ACTION_NOT_FOUND}
        _audit(payload, r, dg)
        return r
    if _replay_hit(payload.click_trans_id, payload.action):
        r = {"error": -8, "error_note": ClickJson.DUPLICATE}
        _audit(payload, r, dg)
        return r
    bad = _bad_sig(payload)
    if bad:
        _audit(payload, bad, dg)
        return bad
    if payload.merchant_prepare_id is None:
        r = {"error": -8, "error_note": ClickJson.BAD_REQUEST}
        _audit(payload, r, dg)
        return r

    with transaction.atomic():
        order = handler.get_order_by_prepare_id(payload.merchant_prepare_id)
        if order is None or str(order.merchant_trans_id) != str(payload.merchant_trans_id):
            r = {"error": -6, "error_note": ClickJson.NO_TX}
            _audit(payload, r, dg)
            return r

        if order.state == ClickOrderState.PAID:
            inner: dict[str, Any] = {"error": -4, "error_note": ClickJson.PAID}
            r = _complete_result(payload, inner, handler, order)
            _audit(payload, r, dg)
            return r
        if order.state == ClickOrderState.CANCELLED:
            inner = {"error": -9, "error_note": ClickJson.CANCELLED}
            r = _complete_result(payload, inner, handler, order)
            _audit(payload, r, dg)
            return r

        try:
            req = amount_to_decimal(payload.amount)
        except Exception:
            inner = {"error": -2, "error_note": ClickJson.BAD_AMOUNT}
            r = _complete_result(payload, inner, handler, order)
            _audit(payload, r, dg)
            return r
        if abs(order.amount - req) > Decimal("0.01"):
            inner = {"error": -2, "error_note": ClickJson.BAD_AMOUNT}
            r = _complete_result(payload, inner, handler, order)
            _audit(payload, r, dg)
            return r

        inner = {"error": 0, "error_note": ClickJson.SUCCESS}
        r = _complete_result(payload, inner, handler, order)
        _audit(payload, r, dg)
        return r
