import httpx
import base64
from constance import config
import logging

logger = logging.getLogger('miab')

def get_basic_auth_headers():
    """
    Returns Authorization header with Basic Auth using Constance config.
    """
    username = config.MIAB_USERNAME
    password = config.MIAB_PASSWORD
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def parse_post(response: httpx.Response):
    if response.status_code != 200:
        return False, response.text
    try:
        data = response.text
        return True, data
    except Exception as e:
        logger.error(f"parse_data error: {e}")
        return False, str(e)

def parse_data(response: httpx.Response):
    if response.status_code != 200:
        return None
    try:
        data = response.json()
        return data
    except Exception as e:
        logger.error(f"parse_get_data error: {e}")
        return None

def get_data(url, params={}, max_retry=3):
    logger.info('[MIAB] get_data: {} - {}'.format(params, max_retry))
    if max_retry <= 0:
        return None
    try:
        response = httpx.get(
            f"{config.MIAB_URL}{url}",
            headers=get_basic_auth_headers(),
            params=params
        )
    except Exception as e:
        logger.error(f"get_data exception: {e}")
        return get_data(url, params, max_retry - 1)

    if response.status_code != 200:
        logger.error('get_data error: {}'.format(response.text))
        return get_data(url, params, max_retry - 1)

    return parse_data(response)


def post_data(url, data={}, max_retry=3, headers={}):
    logger.info('[MIAB] post_data: {} - {}'.format(data, max_retry))
    
    try:
        # Merge basic auth with any custom headers
        request_headers = get_basic_auth_headers()
        if headers:
            request_headers.update(headers)
        
        # Explicitly set Content-Type for form-urlencoded  
        if 'Content-Type' not in request_headers:
            request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        response = httpx.post(
            f"{config.MIAB_URL}{url}",
            headers=request_headers,
            data=data
        )
        
    except Exception as e:
        logger.error(f"post_data exception: {e} - retry: {max_retry}")
        print(f"post_data exception: {e} - retry: {max_retry}")
        if max_retry - 1 <= 0:
            return parse_post(response)
        return post_data(url, data, max_retry - 1, headers)

    if response.status_code != 200:
        logger.error('post_data error: {}'.format(response.text))
        if max_retry - 1 <= 0:
            return parse_post(response)
        return post_data(url, data, max_retry - 1, headers)
    
    return parse_post(response)


# Example function for Mail-in-a-Box API
def list_mail_users():
    return get_data("/admin/mail/users") or []

def add_mail_user(email, password):
    data = {
        "email": email,
        "password": password,
        "privileges": ""
    }
    return post_data("/admin/mail/users/add", data)

def set_mail_user_password(email, password):
    data = {
        "email": email,
        "password": password,
    }
    return post_data("/admin/mail/users/password", data)