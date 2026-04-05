"""Production-oriented checks before handling Click webhooks (HTTPS, source IP)."""

from __future__ import annotations

import ipaddress
import logging

from django.conf import settings
from django.http import HttpRequest, JsonResponse

from click_uz.config import get_click
from click_uz.constants import ClickJson

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str | None:
    """Best-effort client IP (reverse proxy: first hop in ``X-Forwarded-For``)."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip() or None
    cf = request.META.get("HTTP_CF_CONNECTING_IP")
    if cf:
        return cf.strip() or None
    addr = request.META.get("REMOTE_ADDR")
    return str(addr).strip() if addr else None


def _strict_in_debug() -> bool:
    return bool(get_click().get("WEBHOOK_STRICT_IN_DEBUG", False))


def _https_required_for_webhook() -> bool:
    """TLS required unless DEBUG with default loose dev behavior, or explicitly disabled."""
    if settings.DEBUG and not _strict_in_debug():
        return False
    c = get_click()
    if "WEBHOOK_REQUIRE_HTTPS" in c:
        return bool(c["WEBHOOK_REQUIRE_HTTPS"])
    return True


def _allowed_cidrs() -> list[str]:
    raw = get_click().get("WEBHOOK_ALLOWED_CIDRS")
    if not raw:
        return []
    if isinstance(raw, str):
        return [x.strip() for x in raw.split(",") if x.strip()]
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    return []


def _ip_allowed(ip: str | None, cidrs: list[str]) -> bool:
    if not cidrs:
        return True
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for item in cidrs:
        try:
            if "/" in item:
                if addr in ipaddress.ip_network(item, strict=False):
                    return True
            elif addr == ipaddress.ip_address(item):
                return True
        except ValueError:
            continue
    return False


def check_webhook_access(request: HttpRequest) -> JsonResponse | None:
    """
    Return a JSON 403 response if the request must be rejected before body parsing.

    * **HTTPS:** required when not in default dev mode (``DEBUG`` and not
      ``WEBHOOK_STRICT_IN_DEBUG``). Set ``SECURE_PROXY_SSL_HEADER`` when TLS terminates at a proxy.
    * **IP allowlist:** if ``CLICK[\"WEBHOOK_ALLOWED_CIDRS\"]`` is non-empty, only those
      networks may call the webhook (use Click’s published egress IPs).
    """
    if _https_required_for_webhook() and not request.is_secure():
        logger.warning(
            "click_uz webhook rejected: TLS required",
            extra={"path": request.path, "ip": get_client_ip(request)},
        )
        return JsonResponse(
            {"error": -8, "error_note": ClickJson.FORBIDDEN},
            status=403,
            json_dumps_params={"ensure_ascii": False},
        )

    cidrs = _allowed_cidrs()
    if cidrs:
        ip = get_client_ip(request)
        if not _ip_allowed(ip, cidrs):
            logger.warning(
                "click_uz webhook rejected: IP not allowlisted",
                extra={"path": request.path, "ip": ip, "allowed": cidrs},
            )
            return JsonResponse(
                {"error": -8, "error_note": ClickJson.FORBIDDEN},
                status=403,
                json_dumps_params={"ensure_ascii": False},
            )
    return None
