from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import AuthToken

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None

        try:
            token_key = token.split(" ")[1]
            auth_token = AuthToken.objects.get(key=token_key)
        except (IndexError, AuthToken.DoesNotExist):
            raise AuthenticationFailed("Invalid or missing token")

        return (auth_token.user, None)
