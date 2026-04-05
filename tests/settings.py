"""Django settings for pytest."""

SECRET_KEY = "test-secret-key"
DEBUG = True
USE_TZ = True
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "click_uz",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CLICK = {
    "SERVICE_ID": 100,
    "MERCHANT_ID": 1,
    "SECRET_KEY": "s3cr3t",
    "USER_ID": 999,
    "HANDLER_CLASS": "tests.dummy_handler.DummyHandler",
    "ENABLE_AUDIT": False,
    "REPLAY_PROTECTION": False,
}
