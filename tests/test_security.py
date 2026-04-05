import hashlib

from click_uz.security import build_shop_sign_string, verify_shop_signature
from click_uz.types import ShopCallbackPayload


def test_prepare_sign_matches_reference_concatenation() -> None:
    """Same field order as click-llc/click-integration-php BasicPaymentsErrors::request_check."""
    payload = ShopCallbackPayload(
        click_trans_id="1",
        service_id=2,
        click_paydoc_id="9",
        merchant_trans_id="ord1",
        amount="10.00",
        action=0,
        error=0,
        error_note="OK",
        sign_time="2020-01-01 00:00:00",
        sign_string="",
        merchant_prepare_id=None,
    )
    secret = "secret"
    raw = (
        str(payload.click_trans_id)
        + str(payload.service_id)
        + secret
        + str(payload.merchant_trans_id)
        + ""
        + str(payload.amount)
        + str(payload.action)
        + str(payload.sign_time)
    )
    expected = hashlib.md5(raw.encode("utf-8")).hexdigest()
    assert build_shop_sign_string(payload, secret) == expected


def test_complete_sign_includes_merchant_prepare_id() -> None:
    payload = ShopCallbackPayload(
        click_trans_id="1",
        service_id=2,
        click_paydoc_id="9",
        merchant_trans_id="ord1",
        amount="10.00",
        action=1,
        error=0,
        error_note="OK",
        sign_time="2020-01-01 00:00:00",
        sign_string="",
        merchant_prepare_id=99,
    )
    secret = "secret"
    raw = "12secretord19910.0012020-01-01 00:00:00"
    expected = hashlib.md5(raw.encode("utf-8")).hexdigest()
    assert build_shop_sign_string(payload, secret) == expected


def test_verify_shop_signature_case_insensitive_hex() -> None:
    payload = ShopCallbackPayload(
        click_trans_id="1",
        service_id=2,
        click_paydoc_id="9",
        merchant_trans_id="ord1",
        amount="10.00",
        action=0,
        error=0,
        error_note="OK",
        sign_time="2020-01-01 00:00:00",
        sign_string=build_shop_sign_string(
            ShopCallbackPayload(
                click_trans_id="1",
                service_id=2,
                click_paydoc_id="9",
                merchant_trans_id="ord1",
                amount="10.00",
                action=0,
                error=0,
                error_note="OK",
                sign_time="2020-01-01 00:00:00",
                sign_string="",
                merchant_prepare_id=None,
            ),
            "secret",
        ).upper(),
        merchant_prepare_id=None,
    )
    assert verify_shop_signature(payload, "secret") is True
