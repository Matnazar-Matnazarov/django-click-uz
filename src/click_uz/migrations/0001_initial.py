from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="ClickWebhookLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name="created at"
                    ),
                ),
                (
                    "click_trans_id",
                    models.CharField(
                        db_index=True, max_length=64, verbose_name="Click transaction id"
                    ),
                ),
                ("action", models.SmallIntegerField(verbose_name="action")),
                (
                    "merchant_trans_id",
                    models.CharField(max_length=255, verbose_name="merchant transaction id"),
                ),
                ("service_id", models.PositiveIntegerField(verbose_name="service id")),
                ("error_code", models.SmallIntegerField(verbose_name="error code")),
                (
                    "request_digest",
                    models.CharField(blank=True, max_length=64, verbose_name="request digest"),
                ),
            ],
            options={
                "verbose_name": "Click webhook log",
                "verbose_name_plural": "Click webhook logs",
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(fields=["click_trans_id", "action"], name="click_uz_webhook_ta")
                ],
            },
        ),
    ]
