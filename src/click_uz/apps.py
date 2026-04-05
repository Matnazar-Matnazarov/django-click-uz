from django.apps import AppConfig, apps
from django.utils.translation import gettext_lazy as _


class ClickUzConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "click_uz"
    verbose_name = _("Click.uz")

    def ready(self) -> None:
        if not apps.is_installed("django.contrib.admin"):
            return
        from django.contrib import admin

        from click_uz.config import admin_disabled, get_click
        from click_uz.exceptions import ClickUzConfigError

        try:
            get_click()
        except ClickUzConfigError:
            return
        if admin_disabled():
            return

        from click_uz.models import ClickWebhookLog

        if admin.site.is_registered(ClickWebhookLog):
            return

        @admin.register(ClickWebhookLog)
        class ClickWebhookLogAdmin(admin.ModelAdmin):
            list_display = (
                "created_at",
                "click_trans_id",
                "action",
                "merchant_trans_id",
                "error_code",
            )
            list_filter = ("action", "error_code")
            search_fields = ("click_trans_id", "merchant_trans_id")
            ordering = ("-created_at",)
