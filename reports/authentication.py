from dataclasses import dataclass

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .services import verify_token


@dataclass(frozen=True)
class ServiceUser:
    is_authenticated: bool = True


class RemoteTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.headers.get("Authorization", "")
        parts = authorization.split()

        if not parts:
            return None

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Dùng Authorization: Bearer <token>.")

        if not verify_token(authorization):
            raise AuthenticationFailed("Token không hợp lệ hoặc đã hết hạn.")

        return ServiceUser(), authorization

    def authenticate_header(self, request):
        return "Bearer"