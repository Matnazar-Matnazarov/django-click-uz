"""Audit log for Click Shop webhooks."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class ClickWebhookLog(models.Model):
    created_at = models.DateTimeField(_("created at"), auto_now_add=True, db_index=True)
    click_trans_id = models.CharField(_("Click transaction id"), max_length=64, db_index=True)
    action = models.SmallIntegerField(_("action"))
    merchant_trans_id = models.CharField(_("merchant transaction id"), max_length=255)
    service_id = models.PositiveIntegerField(_("service id"))
    error_code = models.SmallIntegerField(_("error code"))
    request_digest = models.CharField(_("request digest"), max_length=64, blank=True)

    class Meta:
        verbose_name = _("Click webhook log")
        verbose_name_plural = _("Click webhook logs")
        ordering = ("-created_at",)
        indexes = (models.Index(fields=("click_trans_id", "action"), name="click_uz_webhook_ta"),)
