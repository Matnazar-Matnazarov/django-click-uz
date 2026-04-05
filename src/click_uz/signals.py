"""Optional Django signals (connect in your app)."""

from __future__ import annotations

import django.dispatch

click_shop_prepare_accepted = django.dispatch.Signal()
click_shop_complete_accepted = django.dispatch.Signal()
