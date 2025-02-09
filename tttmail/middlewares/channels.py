from django.db import close_old_connections
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt


@database_sync_to_async
def get_user(token):
    User = get_user_model()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    user = User.objects.get(pk=payload['user_id'])
    return user

class ChannelsTokenAuthMiddleware:
    """
    Custom token auth middleware
    """
 
    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app
 
    async def __call__(self, scope, receive, send):
 
        # Close old database connections to prevent usage of timed out connections
        close_old_connections()
 
        # Get the token
 
        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            token = ([y for x,y in scope['headers'] if x == b'cookie'][0]).decode('utf-8').split('; ')
            token = [i for i in token if 'auth._token.local=JWT%20' in i][0].replace('auth._token.local=JWT%20','').encode('utf-8')
            scope['user'] = await get_user(token)

        except KeyError as e:
            print(e)
            return None
 
        # Return the inner application directly and let it run everything else
        # return self.app(dict(scope, user=user))
        return await self.app(scope, receive, send)