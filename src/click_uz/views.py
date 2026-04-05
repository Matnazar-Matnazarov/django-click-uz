"""Click Shop HTTP endpoints (CSRF-exempt)."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from click_uz.config import resolve_merchant
from click_uz.constants import ClickJson
from click_uz.exceptions import ClickUzConfigError
from click_uz.handlers import BaseClickShopHandler
from click_uz.integration import get_shop_handler
from click_uz.signals import click_shop_complete_accepted, click_shop_prepare_accepted
from click_uz.types import ShopCallbackPayload
from click_uz.webhook_guard import check_webhook_access
from click_uz.webhooks import process_shop_complete, process_shop_prepare

logger = logging.getLogger(__name__)


class ClickWebhookAccessMixin:
    """HTTPS (production) + optional IP allowlist — see ``CLICK`` / ``click_uz.webhook_guard``."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        denied = check_webhook_access(request)
        if denied is not None:
            return denied
        return super().dispatch(request, *args, **kwargs)


def _parse_body(request: HttpRequest) -> dict[str, Any]:
    if request.POST:
        return dict(request.POST.items())
    raw = request.body.decode("utf-8") if request.body else ""
    if not raw.strip():
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("body must be a JSON object")
    return data


class ClickShopViewMixin:
    def get_shop_handler_for_request(self, request: HttpRequest) -> BaseClickShopHandler:
        return get_shop_handler()


def _handler_getter(
    view: ClickShopViewMixin, request: HttpRequest
) -> Callable[[], BaseClickShopHandler]:
    def getter() -> BaseClickShopHandler:
        return view.get_shop_handler_for_request(request)

    return getter


@method_decorator(csrf_exempt, name="dispatch")
class ClickPrepareView(ClickWebhookAccessMixin, ClickShopViewMixin, View):
    def post(self, request: HttpRequest) -> JsonResponse:
        return _prepare(request, None, _handler_getter(self, request))


@method_decorator(csrf_exempt, name="dispatch")
class ClickCompleteView(ClickWebhookAccessMixin, ClickShopViewMixin, View):
    def post(self, request: HttpRequest) -> JsonResponse:
        return _complete(request, None, _handler_getter(self, request))


@method_decorator(csrf_exempt, name="dispatch")
class ClickShopDispatchView(ClickWebhookAccessMixin, ClickShopViewMixin, View):
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data = _parse_body(request)
            act = data.get("action")
            action = int(act) if act not in (None, "") else None
        except (TypeError, ValueError, json.JSONDecodeError):
            return JsonResponse({"error": -8, "error_note": ClickJson.BAD_REQUEST})
        if action is None:
            return JsonResponse({"error": -8, "error_note": ClickJson.BAD_REQUEST})
        get_handler = _handler_getter(self, request)
        if action == 0:
            return _prepare(request, data, get_handler)
        if action == 1:
            return _complete(request, data, get_handler)
        return JsonResponse({"error": -3, "error_note": ClickJson.ACTION_NOT_FOUND})


@method_decorator(csrf_exempt, name="dispatch")
class ClickWebhookView(ClickShopDispatchView):
    def get_shop_handler_for_request(self, request: HttpRequest) -> BaseClickShopHandler:
        return get_shop_handler(view=self)


def _prepare(
    request: HttpRequest,
    data: dict[str, Any] | None,
    handler_getter: Callable[[], BaseClickShopHandler],
) -> JsonResponse:
    try:
        parsed = data if data is not None else _parse_body(request)
        payload = ShopCallbackPayload.from_request_mapping(parsed)
        resolve_merchant(payload.service_id)
        handler = handler_getter()
        result = process_shop_prepare(payload, handler)
        if result.get("error") == 0:
            click_shop_prepare_accepted.send(
                sender=ClickPrepareView,
                payload=payload,
                merchant_alias="default",
                result=result,
            )
        return JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, ClickUzConfigError) as exc:
        logger.warning("click prepare: %s", exc)
        return JsonResponse({"error": -8, "error_note": ClickJson.BAD_REQUEST})


def _complete(
    request: HttpRequest,
    data: dict[str, Any] | None,
    handler_getter: Callable[[], BaseClickShopHandler],
) -> JsonResponse:
    try:
        parsed = data if data is not None else _parse_body(request)
        payload = ShopCallbackPayload.from_request_mapping(parsed)
        resolve_merchant(payload.service_id)
        handler = handler_getter()
        result = process_shop_complete(payload, handler)
        if result.get("error") == 0:
            click_shop_complete_accepted.send(
                sender=ClickCompleteView,
                payload=payload,
                merchant_alias="default",
                result=result,
            )
        return JsonResponse(result, json_dumps_params={"ensure_ascii": False})
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, ClickUzConfigError) as exc:
        logger.warning("click complete: %s", exc)
        return JsonResponse({"error": -8, "error_note": ClickJson.BAD_REQUEST})
