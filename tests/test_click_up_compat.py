from decimal import Decimal

from django.test import override_settings

from click_uz.config import get_click, merchant_config


def test_flat_click_star_settings() -> None:
    with override_settings(
        CLICK=None,
        CLICK_SERVICE_ID=77,
        CLICK_MERCHANT_ID=2,
        CLICK_SECRET_KEY="k",
        CLICK_USER_ID=5,
        CLICK_HANDLER_CLASS="tests.dummy_handler.DummyHandler",
    ):
        c = get_click()
        assert c["SERVICE_ID"] == 77
        assert merchant_config().service_id == 77


def test_click_up_generate_pay_link_unique() -> None:
    from click_up import ClickUp

    link = ClickUp().initializer.generate_pay_link(
        id=1, amount=Decimal("10.00"), return_url="https://x.test"
    )
    assert "transaction_param=1-" in link
    assert link.count("transaction_param=") == 1


def test_click_up_generate_pay_link_stable_id() -> None:
    from click_up import ClickUp

    link = ClickUp().initializer.generate_pay_link(
        id=99,
        amount=100,
        return_url=None,
        unique_transaction_id=False,
    )
    assert "transaction_param=99" in link
    assert "transaction_param=99-" not in link


def test_click_up_generate_pay_link_explicit_transaction_param() -> None:
    from click_up import ClickUp

    link = ClickUp().initializer.generate_pay_link(
        id=1,
        amount=10,
        transaction_param="1-deadbeefcafe",
    )
    assert "transaction_param=1-deadbeefcafe" in link
