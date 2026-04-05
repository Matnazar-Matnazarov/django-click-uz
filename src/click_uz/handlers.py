"""Application hooks for Shop API (prepare / complete)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from click_uz.types import ShopCallbackPayload


class ClickOrderState(StrEnum):
    PENDING = "pending"
    WAITING = "waiting"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class ClickOrderSnapshot:
    """Minimal order view the Shop callback processor needs."""

    id: int
    merchant_trans_id: str
    amount: Decimal
    state: ClickOrderState


class BaseClickShopHandler(ABC):
    """Subclass and set ``CLICK[\"HANDLER_CLASS\"]`` to your dotted path."""

    @abstractmethod
    def get_order_by_merchant_trans_id(self, merchant_trans_id: str) -> ClickOrderSnapshot | None:
        """Return the order for this `transaction_param` / merchant order id."""

    @abstractmethod
    def get_order_by_prepare_id(self, merchant_prepare_id: int) -> ClickOrderSnapshot | None:
        """Used on complete (action=1) to ensure `merchant_prepare_id` is valid."""

    @abstractmethod
    def on_prepare_success(
        self,
        order: ClickOrderSnapshot,
        payload: ShopCallbackPayload,
    ) -> int:
        """Persist WAITING (or equivalent) and return `merchant_prepare_id` for Click."""

    @abstractmethod
    def on_complete_success(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> None:
        """Mark the order as paid when Click reports a successful completion."""

    @abstractmethod
    def on_complete_reject(self, order: ClickOrderSnapshot, payload: ShopCallbackPayload) -> None:
        """Mark the order as cancelled / rejected (Click `error` < 0 on complete)."""
