import pytest

from tests import dummy_handler


@pytest.fixture(autouse=True)
def _reset_dummy_store() -> None:
    dummy_handler.reset_store()
