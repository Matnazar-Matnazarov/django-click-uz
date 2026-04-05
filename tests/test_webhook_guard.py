import json

import pytest
from django.test import RequestFactory, override_settings

from click_uz.views import ClickPrepareView


def _prepare_body() -> dict:
    from click_uz.security import build_shop_sign_string
    from click_uz.types import ShopCallbackPayload

    p = ShopCallbackPayload(
        click_trans_id="1",
        service_id=100,
        click_paydoc_id="1",
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
        "click_trans_id": p.click_trans_id,
        "service_id": p.service_id,
        "click_paydoc_id": p.click_paydoc_id,
        "merchant_trans_id": p.merchant_trans_id,
        "amount": p.amount,
        "action": p.action,
        "error": p.error,
        "error_note": p.error_note,
        "sign_time": p.sign_time,
        "sign_string": build_shop_sign_string(p, "s3cr3t"),
    }


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_production_rejects_plain_http() -> None:
    factory = RequestFactory()
    req = factory.post(
        "/click/prepare/",
        data=json.dumps(_prepare_body()),
        content_type="application/json",
        secure=False,
    )
    resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 403
    data = json.loads(resp.content.decode())
    assert data["error"] == -8


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_production_accepts_https() -> None:
    factory = RequestFactory()
    req = factory.post(
        "/click/prepare/",
        data=json.dumps(_prepare_body()),
        content_type="application/json",
        secure=True,
    )
    resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_debug_allows_http_by_default() -> None:
    factory = RequestFactory()
    req = factory.post(
        "/click/prepare/",
        data=json.dumps(_prepare_body()),
        content_type="application/json",
        secure=False,
    )
    resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_strict_in_debug_enforces_https() -> None:
    factory = RequestFactory()
    req = factory.post(
        "/click/prepare/",
        data=json.dumps(_prepare_body()),
        content_type="application/json",
        secure=False,
    )
    with override_settings(
        CLICK={
            "SERVICE_ID": 100,
            "MERCHANT_ID": 1,
            "SECRET_KEY": "s3cr3t",
            "USER_ID": 999,
            "HANDLER_CLASS": "tests.dummy_handler.DummyHandler",
            "ENABLE_AUDIT": False,
            "REPLAY_PROTECTION": False,
            "WEBHOOK_STRICT_IN_DEBUG": True,
        }
    ):
        resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_ip_allowlist_blocks_unknown() -> None:
    factory = RequestFactory()
    body = _prepare_body()
    req = factory.post(
        "/click/prepare/",
        data=json.dumps(body),
        content_type="application/json",
        secure=True,
        REMOTE_ADDR="198.51.100.99",
    )
    with override_settings(
        CLICK={
            "SERVICE_ID": 100,
            "MERCHANT_ID": 1,
            "SECRET_KEY": "s3cr3t",
            "USER_ID": 999,
            "HANDLER_CLASS": "tests.dummy_handler.DummyHandler",
            "ENABLE_AUDIT": False,
            "REPLAY_PROTECTION": False,
            "WEBHOOK_ALLOWED_CIDRS": ["203.0.113.0/24"],
        }
    ):
        resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_ip_allowlist_allows_match() -> None:
    factory = RequestFactory()
    body = _prepare_body()
    req = factory.post(
        "/click/prepare/",
        data=json.dumps(body),
        content_type="application/json",
        secure=True,
        REMOTE_ADDR="203.0.113.50",
    )
    with override_settings(
        CLICK={
            "SERVICE_ID": 100,
            "MERCHANT_ID": 1,
            "SECRET_KEY": "s3cr3t",
            "USER_ID": 999,
            "HANDLER_CLASS": "tests.dummy_handler.DummyHandler",
            "ENABLE_AUDIT": False,
            "REPLAY_PROTECTION": False,
            "WEBHOOK_ALLOWED_CIDRS": ["203.0.113.0/24"],
        }
    ):
        resp = ClickPrepareView.as_view()(req)
    assert resp.status_code == 200
