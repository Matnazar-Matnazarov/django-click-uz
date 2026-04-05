# Installation

Requires **Python 3.12+** and **Django 5.0+**.

```bash
pip install django-click-uz
```

Add the app to `INSTALLED_APPS` (use **`click_uz`** only — not `click_up`):

```python
INSTALLED_APPS = [
    # ...
    "click_uz",
]
```

Run migrations:

```bash
python manage.py migrate
```

Include URLs (example):

```python
urlpatterns = [
    path("payment/click/", include("click_uz.urls")),
]
```

See [Configuration](configuration.md) and the GitHub README for `CLICK` settings and webhook setup.
