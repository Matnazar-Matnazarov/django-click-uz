"""Click Shop JSON responses — keep English strings (gateway protocol)."""

from __future__ import annotations


class ClickJson:
    SUCCESS = "Success"
    ACTION_NOT_FOUND = "Action not found"
    DUPLICATE = "Duplicate request"
    BAD_REQUEST = "Error in request from click"
    NO_USER = "User does not exist"
    PAID = "Already paid"
    CANCELLED = "Transaction cancelled"
    BAD_AMOUNT = "Incorrect parameter amount"
    NO_TX = "Transaction does not exist"
    SIGN_FAILED = "SIGN CHECK FAILED!"
    FORBIDDEN = "Forbidden"
