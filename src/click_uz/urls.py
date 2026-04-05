"""URL routes for Click Shop callbacks."""

from __future__ import annotations

from django.urls import path

from click_uz import views

app_name = "click_uz"

urlpatterns = [
    path("prepare/", views.ClickPrepareView.as_view(), name="prepare"),
    path("complete/", views.ClickCompleteView.as_view(), name="complete"),
    path("callback/", views.ClickShopDispatchView.as_view(), name="dispatch"),
    # One URL for both prepare & complete (recommended for click-pkg–style setup):
    path("webhook/", views.ClickWebhookView.as_view(), name="webhook"),
]
