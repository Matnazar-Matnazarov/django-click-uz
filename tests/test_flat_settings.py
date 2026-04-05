import pytest
from django.test import override_settings

from click_uz.config import get_click, handler_path
from click_uz.exceptions import ClickUzConfigError


def test_click_dict_minimal_handler() -> None:
    with override_settings(
        CLICK={
            "SERVICE_ID": 100,
            "MERCHANT_ID": 1,
            "SECRET_KEY": "secret",
            "USER_ID": 42,
            "HANDLER_CLASS": "tests.dummy_handler.DummyHandler",
        }
    ):
        assert get_click()["SERVICE_ID"] == 100
        assert handler_path() == "tests.dummy_handler.DummyHandler"


def test_click_auto_model_handler_path() -> None:
    with override_settings(
        CLICK={
            "SERVICE_ID": 1,
            "MERCHANT_ID": 1,
            "SECRET_KEY": "x",
            "ACCOUNT_MODEL": "auth.User",
            "AMOUNT_FIELD": "id",
            "STATUS_FIELD": "username",
        }
    ):
        assert handler_path() == "click_uz.model_handler.ModelOrderHandler"


def test_click_missing_required() -> None:
    with override_settings(CLICK={}):
        with pytest.raises(ClickUzConfigError):
            get_click()
