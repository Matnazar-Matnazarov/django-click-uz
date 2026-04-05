"""Legacy-style webhook base class."""

from __future__ import annotations

from click_uz.handlers import ClickOrderSnapshot
from click_uz.types import ShopCallbackPayload
from click_uz.utils import payment_params_dict
from click_uz.views import ClickWebhookView


class ClickWebhook(ClickWebhookView):
    """
    Override ``successfully_payment`` / ``cancelled_payment`` / ``prepare_accepted``.

    ``params`` includes snapshot fields and ``payload`` (Click subset).
    """

    def click_prepare_accepted(
        self, snapshot: ClickOrderSnapshot, payload: ShopCallbackPayload
    ) -> None:
        self.prepare_accepted(payment_params_dict(snapshot, payload))

    def click_payment_success(
        self, snapshot: ClickOrderSnapshot, payload: ShopCallbackPayload
    ) -> None:
        self.successfully_payment(payment_params_dict(snapshot, payload))

    def click_payment_cancelled(
        self, snapshot: ClickOrderSnapshot, payload: ShopCallbackPayload
    ) -> None:
        self.cancelled_payment(payment_params_dict(snapshot, payload))

    def prepare_accepted(self, params: dict) -> None:
        pass

    def successfully_payment(self, params: dict) -> None:
        pass

    def cancelled_payment(self, params: dict) -> None:
        pass


__all__ = ["ClickWebhook"]
