"""In-memory handler for package tests."""

from __future__ import annotations

from decimal import Decimal

from click_uz.handlers import BaseClickShopHandler, ClickOrderSnapshot, ClickOrderState
from click_uz.types import ShopCallbackPayload

_store: dict[int, ClickOrderSnapshot] = {}


def reset_store() -> None:
    _store.clear()
    _store[42] = ClickOrderSnapshot(
        id=42,
        merchant_trans_id="o1",
        amount=Decimal("100.00"),
        state=ClickOrderState.PENDING,
    )


reset_store()


class DummyHandler(BaseClickShopHandler):
    def get_order_by_merchant_trans_id(self, merchant_trans_id: str) -> ClickOrderSnapshot | None:
        for row in _store.values():
            if str(row.merchant_trans_id) == str(merchant_trans_id):
                return row
        return None

    def get_order_by_prepare_id(self, merchant_prepare_id: int) -> ClickOrderSnapshot | None:
        return _store.get(int(merchant_prepare_id))

    def on_prepare_success(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> int:
        _store[order.id] = ClickOrderSnapshot(
            id=order.id,
            merchant_trans_id=order.merchant_trans_id,
            amount=order.amount,
            state=ClickOrderState.WAITING,
        )
        return order.id

    def on_complete_success(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> None:
        _store[order.id] = ClickOrderSnapshot(
            id=order.id,
            merchant_trans_id=order.merchant_trans_id,
            amount=order.amount,
            state=ClickOrderState.PAID,
        )

    def on_complete_reject(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> None:
        _store[order.id] = ClickOrderSnapshot(
            id=order.id,
            merchant_trans_id=order.merchant_trans_id,
            amount=order.amount,
            state=ClickOrderState.CANCELLED,
        )
