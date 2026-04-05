from __future__ import annotations

from typing import Any

from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from click_uz.config import handler_path
from click_uz.exceptions import ClickUzConfigError
from click_uz.handlers import BaseClickShopHandler
from click_uz.model_handler import ModelOrderHandler


def get_shop_handler(view: Any | None = None) -> BaseClickShopHandler:
    obj = import_string(handler_path())
    if isinstance(obj, type) and issubclass(obj, BaseClickShopHandler):
        if issubclass(obj, ModelOrderHandler):
            return obj(view=view)
        return obj()
    if isinstance(obj, BaseClickShopHandler):
        return obj
    raise ClickUzConfigError(
        _("HANDLER_CLASS must be a BaseClickShopHandler subclass or instance.")
    )
