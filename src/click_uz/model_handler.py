"""Default handler: order model + CLICK[ACCOUNT_MODEL|AMOUNT_FIELD|STATUS_FIELD]."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.apps import apps
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from click_uz.config import commission_percent, get_click
from click_uz.exceptions import ClickUzConfigError
from click_uz.handlers import BaseClickShopHandler, ClickOrderSnapshot, ClickOrderState
from click_uz.types import ShopCallbackPayload


def _model_cls(path: str) -> type[Any]:
    parts = path.split(".")
    if len(parts) < 2:
        raise ClickUzConfigError(_("ACCOUNT_MODEL must be like 'orders.Order'."))
    return apps.get_model(parts[0], parts[-1])


class ModelOrderHandler(BaseClickShopHandler):
    def __init__(self, view: Any | None = None) -> None:
        self._view = view
        c = get_click()
        self._model = _model_cls(str(c["ACCOUNT_MODEL"]))
        self._amount_f = str(c["AMOUNT_FIELD"])
        self._status_f = str(c["STATUS_FIELD"])
        self._pending = str(c.get("STATUS_PENDING") or "pending")
        self._waiting = str(c.get("STATUS_WAITING") or "waiting_payment")
        self._paid = str(c.get("STATUS_PAID") or "paid")
        self._cancelled = str(c.get("STATUS_CANCELLED") or "cancelled")
        tf = c.get("MERCHANT_TRANS_FIELD")
        self._trans_f = str(tf) if tf else None
        self._pct = commission_percent()

    def _base_amount(self, order: Any) -> Decimal:
        v = getattr(order, self._amount_f)
        return v if isinstance(v, Decimal) else Decimal(str(v))

    def payable_amount(self, order: Any) -> Decimal:
        base = self._base_amount(order)
        if self._pct <= 0:
            return base
        return (base * (Decimal("1") + self._pct / Decimal("100"))).quantize(Decimal("0.01"))

    def _state(self, order: Any) -> ClickOrderState:
        s = str(getattr(order, self._status_f))
        if s == self._paid:
            return ClickOrderState.PAID
        if s == self._cancelled:
            return ClickOrderState.CANCELLED
        if s == self._waiting:
            return ClickOrderState.WAITING
        return ClickOrderState.PENDING

    def _snap(self, order: Any) -> ClickOrderSnapshot:
        tid = str(getattr(order, self._trans_f)) if self._trans_f else str(order.pk)
        return ClickOrderSnapshot(
            id=int(order.pk),
            merchant_trans_id=tid,
            amount=self.payable_amount(order),
            state=self._state(order),
        )

    def _row(self, pk: int) -> Any | None:
        return self._model.objects.filter(pk=pk).first()

    def get_order_by_merchant_trans_id(self, merchant_trans_id: str) -> ClickOrderSnapshot | None:
        if self._trans_f:
            row = self._model.objects.filter(**{self._trans_f: merchant_trans_id}).first()
        else:
            try:
                row = self._row(int(str(merchant_trans_id).strip()))
            except (TypeError, ValueError):
                row = None
        return self._snap(row) if row else None

    def get_order_by_prepare_id(self, merchant_prepare_id: int) -> ClickOrderSnapshot | None:
        row = self._row(int(merchant_prepare_id))
        return self._snap(row) if row else None

    def on_prepare_success(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> int:
        with transaction.atomic():
            obj = self._model.objects.select_for_update().filter(pk=order.id).first()
            if obj is None:
                return order.id
            setattr(obj, self._status_f, self._waiting)
            obj.save(update_fields=[self._status_f])
        self._hook(("click_prepare_accepted",), self._snap(obj), payload)
        return int(order.id)

    def on_complete_success(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> None:
        with transaction.atomic():
            obj = self._model.objects.select_for_update().filter(pk=order.id).first()
            if obj is None:
                return
            setattr(obj, self._status_f, self._paid)
            obj.save(update_fields=[self._status_f])
        self._hook(("click_payment_success", "successfully_payment"), self._snap(obj), payload)

    def on_complete_reject(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> None:
        with transaction.atomic():
            obj = self._model.objects.select_for_update().filter(pk=order.id).first()
            if obj is None:
                self._hook(("click_payment_cancelled", "cancelled_payment"), order, payload)
                return
            setattr(obj, self._status_f, self._cancelled)
            obj.save(update_fields=[self._status_f])
        self._hook(("click_payment_cancelled", "cancelled_payment"), self._snap(obj), payload)

    def _hook(self, names: tuple[str, ...], snap: Any, payload: ShopCallbackPayload) -> None:
        if self._view is None:
            return
        for n in names:
            fn = getattr(self._view, n, None)
            if callable(fn):
                fn(snap, payload)
                return
