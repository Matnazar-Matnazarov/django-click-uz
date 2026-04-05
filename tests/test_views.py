import json

import pytest
from django.test import RequestFactory

from click_uz.security import build_shop_sign_string
from click_uz.types import ShopCallbackPayload
from click_uz.views import ClickPrepareView, ClickShopDispatchView


def _signed_prepare_body() -> dict[str, object]:
    payload = ShopCallbackPayload(
        click_trans_id="777",
        service_id=100,
        click_paydoc_id="888",
        merchant_trans_id="o1",
        amount="100.00",
        action=0,
        error=0,
        error_note="Success",
        sign_time="2024-01-15 12:00:00",
        sign_string="",
        merchant_prepare_id=None,
    )
    return {
        "click_trans_id": payload.click_trans_id,
        "service_id": payload.service_id,
        "click_paydoc_id": payload.click_paydoc_id,
        "merchant_trans_id": payload.merchant_trans_id,
        "amount": payload.amount,
        "action": payload.action,
        "error": payload.error,
        "error_note": payload.error_note,
        "sign_time": payload.sign_time,
        "sign_string": build_shop_sign_string(payload, "s3cr3t"),
    }


@pytest.mark.django_db
def test_prepare_view_json_success() -> None:
    factory = RequestFactory()
    body = _signed_prepare_body()
    req = factory.post(
        "/payments/click/prepare/",
        data=json.dumps(body),
        content_type="application/json",
    )
    resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 200
    data = json.loads(resp.content.decode())
    assert data["error"] == 0
    assert data["merchant_prepare_id"] == 42


@pytest.mark.django_db
def test_dispatch_view_reuses_json_body() -> None:
    """Regression: JSON body must not be read twice when using the dispatch URL."""
    factory = RequestFactory()
    body = _signed_prepare_body()
    req = factory.post(
        "/payments/click/callback/",
        data=json.dumps(body),
        content_type="application/json",
    )
    resp = ClickShopDispatchView.as_view()(req)
    assert resp.status_code == 200
    data = json.loads(resp.content.decode())
    assert data["error"] == 0
