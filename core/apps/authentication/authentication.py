from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from ninja.security import APIKeyHeader
from django.http import HttpRequest

User = get_user_model()


class APIKeyAuthentication(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request: HttpRequest, key: str):
        try:
            user = User.objects.get(api_key=key, is_api_key_active=True)
            return user
        except User.DoesNotExist:
            return None


# Create global instance
api_key_auth = APIKeyAuthentication()
