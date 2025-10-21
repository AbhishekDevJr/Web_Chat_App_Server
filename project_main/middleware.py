from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user_from_token(token_key):
    from rest_framework.authtoken.models import Token
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()
    
class TokenAuthMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope.get("type") == "websocket":
            print(f'Server Logs: Query String Auth {scope.get("query_string", b"")}')
            qs = scope.get("query_string", b"").decode()
            params = parse_qs(qs)
            token_list = params.get("token") or params.get("auth_token")
            if token_list:
                token_key = token_list[0]
                scope["user"] = await get_user_from_token(token_key)
            else:
                scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
