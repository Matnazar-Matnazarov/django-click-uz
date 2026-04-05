"""Click.uz integration errors."""


class ClickUzError(Exception):
    """Base error for this package."""


class ClickUzConfigError(ClickUzError):
    """Invalid or missing Django settings / merchant configuration."""


class ClickUzAPIError(ClickUzError):
    """Merchant API returned an error or unexpected response."""

    def __init__(
        self, message: str, *, status_code: int | None = None, body: str | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body
