"""Resolve Click config from ``CLICK`` dict and/or legacy ``CLICK_*`` module-level settings."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from click_uz.exceptions import ClickUzConfigError

SETTINGS_KEY = "CLICK"


@dataclass(frozen=True, slots=True)
class ClickMerchantConfig:
    merchant_id: int
    service_id: int
    secret_key: str
    click_user_id: int
    merchant_user_id: int | None = None
    merchant_api_base: str = "https://api.click.uz/v2/merchant/"
    pay_base_url: str = "https://my.click.uz/services/pay"


def _from_flat_module_settings() -> dict[str, Any] | None:
    if not hasattr(settings, "CLICK_SERVICE_ID"):
        return None
    s = settings
    m: dict[str, Any] = {
        "SERVICE_ID": s.CLICK_SERVICE_ID,
        "MERCHANT_ID": s.CLICK_MERCHANT_ID,
        "SECRET_KEY": s.CLICK_SECRET_KEY,
    }
    pairs = (
        ("CLICK_USER_ID", "USER_ID"),
        ("CLICK_ACCOUNT_MODEL", "ACCOUNT_MODEL"),
        ("CLICK_AMOUNT_FIELD", "AMOUNT_FIELD"),
        ("CLICK_STATUS_FIELD", "STATUS_FIELD"),
        ("CLICK_HANDLER_CLASS", "HANDLER_CLASS"),
        ("CLICK_MERCHANT_USER_ID", "MERCHANT_USER_ID"),
        ("CLICK_COMMISSION_PERCENT", "COMMISSION_PERCENT"),
        ("CLICK_DISABLE_ADMIN", "DISABLE_ADMIN"),
        ("CLICK_ENABLE_AUDIT", "ENABLE_AUDIT"),
        ("CLICK_REPLAY_PROTECTION", "REPLAY_PROTECTION"),
        ("CLICK_REPLAY_CACHE_TTL", "REPLAY_CACHE_TTL"),
        ("CLICK_API_BASE", "API_BASE"),
        ("CLICK_PAY_URL", "PAY_URL"),
        ("CLICK_WEBHOOK_REQUIRE_HTTPS", "WEBHOOK_REQUIRE_HTTPS"),
        ("CLICK_WEBHOOK_STRICT_IN_DEBUG", "WEBHOOK_STRICT_IN_DEBUG"),
        ("CLICK_WEBHOOK_ALLOWED_CIDRS", "WEBHOOK_ALLOWED_CIDRS"),
    )
    for attr, key in pairs:
        if hasattr(s, attr):
            val = getattr(s, attr)
            if val is not None and val != "":
                m[key] = val
    return m


def get_click() -> dict[str, Any]:
    raw = getattr(settings, SETTINGS_KEY, None)
    if (
        isinstance(raw, dict)
        and raw.get("SERVICE_ID") not in (None, "")
        and raw.get("MERCHANT_ID")
        not in (
            None,
            "",
        )
        and raw.get("SECRET_KEY") not in (None, "")
    ):
        return dict(raw)
    flat = _from_flat_module_settings()
    if flat is None:
        raise ClickUzConfigError(
            _(
                "Set CLICK = {SERVICE_ID, MERCHANT_ID, SECRET_KEY, ...} or define "
                "CLICK_SERVICE_ID, CLICK_MERCHANT_ID, CLICK_SECRET_KEY on settings."
            )
        )
    for key in ("SERVICE_ID", "MERCHANT_ID", "SECRET_KEY"):
        if flat.get(key) in (None, ""):
            raise ClickUzConfigError(
                _("CLICK_SERVICE_ID / CLICK_MERCHANT_ID / CLICK_SECRET_KEY are required.")
            )
    return flat


def merchant_config() -> ClickMerchantConfig:
    c = get_click()
    uid = c.get("USER_ID")
    return ClickMerchantConfig(
        merchant_id=int(c["MERCHANT_ID"]),
        service_id=int(c["SERVICE_ID"]),
        secret_key=str(c["SECRET_KEY"]),
        click_user_id=int(uid if uid is not None else c["MERCHANT_ID"]),
        merchant_user_id=int(c["MERCHANT_USER_ID"])
        if c.get("MERCHANT_USER_ID") not in (None, "")
        else None,
        merchant_api_base=str(c.get("API_BASE") or "https://api.click.uz/v2/merchant/").rstrip("/")
        + "/",
        pay_base_url=str(c.get("PAY_URL") or "https://my.click.uz/services/pay"),
    )


def resolve_merchant(service_id: int) -> tuple[str, ClickMerchantConfig]:
    cfg = merchant_config()
    if int(cfg.service_id) != int(service_id):
        raise ClickUzConfigError(_("Incoming service_id does not match configured SERVICE_ID."))
    return "default", cfg


def handler_path() -> str:
    c = get_click()
    hc = c.get("HANDLER_CLASS")
    if hc:
        return str(hc)
    if c.get("ACCOUNT_MODEL") and c.get("AMOUNT_FIELD") is not None:
        if not c.get("STATUS_FIELD"):
            raise ClickUzConfigError(
                _("When using ACCOUNT_MODEL, set STATUS_FIELD (CharField) for payment state.")
            )
        return "click_uz.model_handler.ModelOrderHandler"
    raise ClickUzConfigError(
        _("Set HANDLER_CLASS or ACCOUNT_MODEL + AMOUNT_FIELD + STATUS_FIELD for webhooks.")
    )


def commission_percent() -> Decimal:
    return Decimal(str(get_click().get("COMMISSION_PERCENT") or 0))


def replay_enabled() -> bool:
    return bool(get_click().get("REPLAY_PROTECTION", False))


def replay_ttl() -> int:
    return int(get_click().get("REPLAY_CACHE_TTL", 86400))


def audit_enabled() -> bool:
    return bool(get_click().get("ENABLE_AUDIT", True))


def admin_disabled() -> bool:
    return bool(get_click().get("DISABLE_ADMIN", False))


get_merchant_config = merchant_config
resolve_merchant_by_service_id = resolve_merchant
