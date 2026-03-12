import hashlib
import hmac
import json
from typing import Any, Dict
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.core.config import get_settings


def _get_telegram_secret_key(bot_token: str) -> bytes:
    return hashlib.sha256(f"WebAppData{bot_token}".encode("utf-8")).digest()


def verify_init_data(init_data: str) -> Dict[str, Any]:
    """
    Validate Telegram WebApp init data according to
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    """
    settings = get_settings()
    bot_token = settings.telegram_bot_token
    if bot_token == "CHANGE_ME":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Telegram bot token is not configured",
        )

    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if received_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing hash in init data",
        )

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = _get_telegram_secret_key(bot_token)
    expected_hash = hmac.new(
        secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    # Parse user payload to ensure we have telegram_id
    user_raw = parsed.get("user")
    if not user_raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user in init data",
        )

    try:
        user_payload = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user payload in init data",
        ) from exc

    if "id" not in user_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user id in init data",
        )

    return {"user": user_payload, "raw": parsed}

