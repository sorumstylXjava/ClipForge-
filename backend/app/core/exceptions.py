"""
ClipForge Backend — Custom HTTP Exceptions
Semua error response menggunakan format standar: { error, message, status }
"""

from fastapi import HTTPException


class ClipForgeException(HTTPException):
    """Base exception untuk semua custom ClipForge errors."""

    def __init__(self, status_code: int, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(status_code=status_code, detail=message)


# ─────────────────────────────────────────────────────────────────────────────
# 401 Unauthorized
# ─────────────────────────────────────────────────────────────────────────────

class UnauthorizedException(ClipForgeException):
    """Token tidak valid atau expired."""

    def __init__(self, message: str = "Token tidak valid atau expired."):
        super().__init__(
            status_code=401,
            error_code="UNAUTHORIZED",
            message=message,
        )


class InvalidCredentialsException(ClipForgeException):
    """Email atau password salah."""

    def __init__(self, message: str = "Email atau password tidak valid."):
        super().__init__(
            status_code=401,
            error_code="INVALID_CREDENTIALS",
            message=message,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 403 Forbidden
# ─────────────────────────────────────────────────────────────────────────────

class ForbiddenException(ClipForgeException):
    """Tidak punya akses ke resource."""

    def __init__(self, message: str = "Anda tidak punya akses ke resource ini."):
        super().__init__(
            status_code=403,
            error_code="FORBIDDEN",
            message=message,
        )


class PremiumRequiredException(ClipForgeException):
    """Fitur membutuhkan Premium Plan."""

    def __init__(self, feature: str = "Fitur ini"):
        super().__init__(
            status_code=403,
            error_code="PLAN_REQUIRED",
            message=f"{feature} membutuhkan Premium Plan.",
        )


class AccountSuspendedException(ClipForgeException):
    """Akun user di-suspend."""

    def __init__(self):
        super().__init__(
            status_code=403,
            error_code="ACCOUNT_SUSPENDED",
            message="Akun Anda telah di-suspend. Hubungi support.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 404 Not Found
# ─────────────────────────────────────────────────────────────────────────────

class NotFoundException(ClipForgeException):
    """Resource tidak ditemukan."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            message=f"{resource} tidak ditemukan.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 409 Conflict
# ─────────────────────────────────────────────────────────────────────────────

class ConflictException(ClipForgeException):
    """Resource sudah ada (misal: email sudah terdaftar)."""

    def __init__(self, message: str = "Resource sudah ada."):
        super().__init__(
            status_code=409,
            error_code="CONFLICT",
            message=message,
        )


class EmailAlreadyExistsException(ClipForgeException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error_code="EMAIL_EXISTS",
            message="Email sudah terdaftar. Silakan login.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 422 Validation Error
# ─────────────────────────────────────────────────────────────────────────────

class ValidationException(ClipForgeException):
    """Input tidak valid."""

    def __init__(self, message: str = "Input tidak valid."):
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message=message,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 429 Rate Limit / Quota
# ─────────────────────────────────────────────────────────────────────────────

class DailyLimitExceededException(ClipForgeException):
    """Kuota harian Free Plan habis."""

    def __init__(self, limit: int = 3):
        super().__init__(
            status_code=429,
            error_code="DAILY_LIMIT",
            message=(
                f"Kuota harian Free Plan habis ({limit} video/hari). "
                "Upgrade ke Premium untuk akses unlimited."
            ),
        )


class RateLimitedException(ClipForgeException):
    """Terlalu banyak request."""

    def __init__(self):
        super().__init__(
            status_code=429,
            error_code="RATE_LIMITED",
            message="Terlalu banyak request. Coba lagi dalam beberapa saat.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 500 Internal
# ─────────────────────────────────────────────────────────────────────────────

class InternalServerException(ClipForgeException):
    def __init__(self, message: str = "Terjadi kesalahan internal. Coba lagi."):
        super().__init__(
            status_code=500,
            error_code="INTERNAL_ERROR",
            message=message,
        )
