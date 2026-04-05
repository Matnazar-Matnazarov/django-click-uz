# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- README.md and README_UZ.md aligned: same sections, badges, and expanded code samples (settings, model, urls, webhook, pay link, security).

## [0.1.1] — 2026-04-06

### Changed

- README: professional layout, Django / Click badges, “what’s in the package” table, local MkDocs instructions.
- Documentation URLs: point to GitHub `docs/` tree; removed ReadTheDocs config and references (no hosted RTD project).

## [0.1.0] — 2026-04-05

### Added

- Django 5+ Click Shop integration: prepare/complete webhooks, pay URL builder, MD5 signature verification.
- `click_uz` app (migrations, optional `ClickWebhookLog` audit, Uzbek locale).
- `click_up` compatibility imports (`ClickUp`, `ClickWebhook`, `generate_pay_link`).
- `CLICK` dict and flat `CLICK_*` settings; `ModelOrderHandler` for order models.
- Webhook guard: HTTPS (production), optional IP allowlist (`WEBHOOK_ALLOWED_CIDRS`).
- PyPI metadata, MkDocs site skeleton, GitHub Actions (CI + tag publish).

[Unreleased]: https://github.com/Matnazar-Matnazarov/django-click-uz/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Matnazar-Matnazarov/django-click-uz/releases/tag/v0.1.1
[0.1.0]: https://github.com/Matnazar-Matnazarov/django-click-uz/releases/tag/v0.1.0
