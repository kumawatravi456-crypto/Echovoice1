"""Issue short-lived ElevenLabs Scribe tokens without exposing provider credentials."""

from __future__ import annotations

import httpx
import logging
import re


TOKEN_URL = "https://api.elevenlabs.io/v1/single-use-token/realtime_scribe"
logger = logging.getLogger(__name__)
MAX_PROVIDER_MESSAGE_LENGTH = 240


def _sanitize_provider_message(value: str, api_key: str) -> str:
    message = re.sub(r"[\r\n\t\x00-\x1f]+", " ", value).strip()
    if api_key:
        message = message.replace(api_key, "[REDACTED]")
    message = re.sub(r"(?i)\bBearer\s+[^\s,;]+", "Bearer [REDACTED]", message)
    message = re.sub(
        r"(?i)\b(xi-api-key|authorization|api[_ -]?key|token)\b['\"]?\s*[:=]\s*['\"]?[^\s,;}'\"]+",
        r"\1=[REDACTED]",
        message,
    )
    message = re.sub(r"\s+", " ", message)
    return message[:MAX_PROVIDER_MESSAGE_LENGTH] or "provider rejected request"


def _provider_error_summary(error: httpx.HTTPStatusError, api_key: str) -> str:
    try:
        payload = error.response.json()
    except (ValueError, UnicodeDecodeError):
        return "provider returned a non-JSON or unreadable error response"

    if not isinstance(payload, dict):
        return "provider returned an error response without structured details"

    detail = payload.get("detail")
    error_object = payload.get("error")
    candidates = [item for item in (detail, error_object, payload) if isinstance(item, dict)]
    code: str | None = None
    message: str | None = detail if isinstance(detail, str) else None
    for candidate in candidates:
        for key in ("status", "code", "error_code"):
            value = candidate.get(key)
            if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
                code = value
                break
        if not message:
            value = candidate.get("message")
            if isinstance(value, str):
                message = value
        if code and message:
            break

    parts = []
    if code:
        parts.append(f"code={code}")
    if message:
        parts.append(f'message="{_sanitize_provider_message(message, api_key)}"')
    return "; ".join(parts) if parts else "provider returned an error response without a safe message or code"


def _provider_error_code(error: httpx.HTTPStatusError) -> str | None:
    try:
        payload = error.response.json()
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    candidates = [payload.get("detail"), payload.get("error"), payload]
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        for field in ("status", "code", "error_code"):
            value = candidate.get(field)
            if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", value):
                return value
    return None


class ScribeTokenConfigurationError(RuntimeError):
    """Raised when the ElevenLabs API key is not configured."""


class ScribeProviderError(RuntimeError):
    """Raised when ElevenLabs cannot issue a short-lived Scribe token."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        provider_code: str | None = None,
        failure_kind: str = "provider",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.provider_code = provider_code
        self.failure_kind = failure_kind


class ScribeTokenService:
    def __init__(self, api_key: str | None, *, client_factory=httpx.AsyncClient) -> None:
        self._api_key = api_key.strip() if api_key else ""
        self._client_factory = client_factory

    async def create_token(self) -> str:
        if not self._api_key:
            raise ScribeTokenConfigurationError("ElevenLabs API key is not configured")
        try:
            async with self._client_factory(timeout=10.0) as client:
                response = await client.post(TOKEN_URL, headers={"xi-api-key": self._api_key})
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as error:
            summary = _provider_error_summary(error, self._api_key)
            provider_code = _provider_error_code(error)
            logger.warning(
                "Scribe token provider rejected request (HTTP %d; %s)",
                error.response.status_code,
                summary,
            )
            raise ScribeProviderError(
                "ElevenLabs could not issue a Scribe token",
                status_code=error.response.status_code,
                provider_code=provider_code,
            ) from error
        except httpx.TimeoutException as error:
            logger.warning("Scribe token provider request timed out")
            raise ScribeProviderError(
                "ElevenLabs token request timed out", failure_kind="timeout"
            ) from error
        except httpx.HTTPError as error:
            logger.warning("Scribe token provider request failed (%s)", type(error).__name__)
            raise ScribeProviderError(
                "ElevenLabs token provider is unreachable", failure_kind="network"
            ) from error
        except ValueError as error:
            logger.warning("Scribe token provider returned an invalid response")
            raise ScribeProviderError(
                "ElevenLabs returned an invalid token response", failure_kind="invalid_response"
            ) from error
        token = payload.get("token") if isinstance(payload, dict) else None
        if not isinstance(token, str) or not token.strip():
            raise ScribeProviderError(
                "ElevenLabs returned an invalid Scribe token", failure_kind="invalid_response"
            )
        return token
