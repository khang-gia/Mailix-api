from django.db import close_old_connections
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

@database_sync_to_async
def get_user(token):
    User = get_user_model()
    try:
        access_token = AccessToken(token)
        user_id = access_token.get('user_id')
        if not user_id:
            print("WS Auth Error: Token has no user_id")
            return None
        
        user = User.objects.get(pk=user_id)
        print(f"WS Auth Success: User {user.username}")
        return user
    except (InvalidToken, TokenError) as e:
        print(f"WS Auth Error: {e}")
        return None
    except User.DoesNotExist:
        print("WS Auth Error: User Does Not Exist")
        return None
    except Exception as e:
        print(f"WS Exception in get_user: {e}")
        return None

class ChannelsTokenAuthMiddleware:
    """
    Custom token auth middleware
    """
 
    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app
 
    async def __call__(self, scope, receive, send):
        close_old_connections()
 
        try:
            # 1. Try Query String (Most reliable for fresh tokens)
            import urllib.parse
            query_params = urllib.parse.parse_qs(scope['query_string'].decode())
            token = query_params.get('token', [None])[0]
            
            if token:
                print(f"WS Token found in Query String")
            else:
                # 2. Fallback to Cookies
                headers = dict(scope['headers'])
                cookie_header = headers.get(b'cookie', b'').decode('utf-8')
                cookies = {k.strip(): urllib.parse.unquote(v) for k, v in [x.split('=', 1) for x in cookie_header.split(';') if '=' in x]}
                
                # Check all possible cookie names
                token = cookies.get('auth:token') or cookies.get('auth_token') or cookies.get('auth._token.local')
                if token:
                    print(f"WS Token found in Cookies")

            if token:
                token = token.replace('JWT ', '').replace('Bearer ', '')
                from django.contrib.auth.models import AnonymousUser
                user = await get_user(token)
                scope['user'] = user or AnonymousUser()
            else:
                print("WS No token found anywhere")
                from django.contrib.auth.models import AnonymousUser
                scope['user'] = AnonymousUser()

        except Exception as e:
            print(f"WS Auth Exception: {e}")
            from django.contrib.auth.models import AnonymousUser
            scope['user'] = AnonymousUser()
 
        return await self.app(scope, receive, send)