"""HTTP client for Click Merchant API (`https://api.click.uz/v2/merchant/`)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Mapping
from decimal import Decimal
from typing import Any
from urllib.parse import quote, urljoin

from click_uz.config import ClickMerchantConfig
from click_uz.exceptions import ClickUzAPIError
from click_uz.security import build_merchant_auth_header


class ClickMerchantClient:
    """Thin JSON client over the documented Merchant API."""

    def __init__(self, cfg: ClickMerchantConfig, *, timeout: int = 30) -> None:
        self._cfg = cfg
        self._timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = urljoin(self._cfg.merchant_api_base, path.lstrip("/"))
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Auth": build_merchant_auth_header(self._cfg),
        }
        data: bytes | None
        if json_body is not None:
            data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        else:
            data = None
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ClickUzAPIError(
                f"Click Merchant API HTTP {exc.code}",
                status_code=exc.code,
                body=body,
            ) from exc
        except urllib.error.URLError as exc:
            raise ClickUzAPIError(f"Click Merchant API connection error: {exc}") from exc
        try:
            out: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ClickUzAPIError("Invalid JSON from Click Merchant API", body=raw) from exc
        return out

    def create_invoice(
        self,
        *,
        amount: Decimal,
        phone_number: str,
        merchant_trans_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "invoice/create",
            json_body={
                "service_id": self._cfg.service_id,
                "amount": float(amount),
                "phone_number": phone_number,
                "merchant_trans_id": merchant_trans_id,
            },
        )

    def check_invoice(self, *, invoice_id: int) -> dict[str, Any]:
        sid = self._cfg.service_id
        return self._request("GET", f"invoice/status/{sid}/{invoice_id}")

    def payment_status(self, *, payment_id: int) -> dict[str, Any]:
        sid = self._cfg.service_id
        return self._request("GET", f"payment/status/{sid}/{payment_id}")

    def payment_status_by_merchant_trans_id(
        self,
        *,
        merchant_trans_id: str,
        payment_date: str,
    ) -> dict[str, Any]:
        """GET .../payment/status_by_mti/:service_id/:merchant_trans_id/:YYYY-MM-DD"""
        sid = self._cfg.service_id
        mt = quote(str(merchant_trans_id), safe="")
        return self._request("GET", f"payment/status_by_mti/{sid}/{mt}/{payment_date}")

    def cancel_payment(self, *, payment_id: int) -> dict[str, Any]:
        sid = self._cfg.service_id
        return self._request("DELETE", f"payment/reversal/{sid}/{payment_id}")

    def fiscal_ofd_data(self, *, payment_id: int) -> dict[str, Any]:
        sid = self._cfg.service_id
        return self._request("GET", f"payment/ofd_data/{sid}/{payment_id}")
