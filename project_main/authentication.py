from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token


class CustomTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        auth = super().authenticate(request)
        
        if auth:
            return auth
        
        token_key = request.COOKIES.get('auth_token')
        
        if not token_key:
            return None
        
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid Token.')
        
        return (token.user, token)