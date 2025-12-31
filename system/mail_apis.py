import httpx
from constance import config
import logging

logger = logging.getLogger('mail_server')

def get_auth_headers():
    """
    Returns Authorization header with Bearer token using Constance config.
    """
    token = config.MAIL_SERVER_TOKEN
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def parse_response(response: httpx.Response):
    """Parse response for POST/PUT/DELETE requests"""
    if response.status_code not in [200, 201]:
        return False, response.text
    try:
        data = response.json() if response.text else {}
        return True, data
    except Exception as e:
        logger.error(f"parse_response error: {e}")
        return False, str(e)


def parse_data(response: httpx.Response):
    """Parse response for GET requests"""
    if response.status_code != 200:
        logger.error(f"parse_data error: {response.status_code} - {response.text}")
        return None
    try:
        data = response.json()
        return data
    except Exception as e:
        logger.error(f"parse_data error: {e}")
        return None


def get_data(url, params={}, max_retry=3):
    """
    GET request to mail server API
    """
    logger.info(f'[MAIL_SERVER] get_data: {url} - params: {params} - retry: {max_retry}')
    if max_retry <= 0:
        return None
    
    try:
        response = httpx.get(
            f"{config.MAIL_SERVER_URL}{url}",
            headers=get_auth_headers(),
            params=params,
            timeout=30.0
        )
    except Exception as e:
        logger.error(f"get_data exception: {e}")
        return get_data(url, params, max_retry - 1)

    if response.status_code != 200:
        logger.error(f'get_data error: {response.status_code} - {response.text}')
        return get_data(url, params, max_retry - 1)

    return parse_data(response)


def post_data(url, data={}, max_retry=3):
    """
    POST request to mail server API
    """
    logger.info(f'[MAIL_SERVER] post_data: {url} - data: {data} - retry: {max_retry}')
    
    try:
        response = httpx.post(
            f"{config.MAIL_SERVER_URL}{url}",
            headers=get_auth_headers(),
            json=data,
            timeout=30.0
        )
    except Exception as e:
        logger.error(f"post_data exception: {e} - retry: {max_retry}")
        if max_retry - 1 <= 0:
            return False, str(e)
        return post_data(url, data, max_retry - 1)

    if response.status_code not in [200, 201]:
        logger.error(f'post_data error: {response.status_code} - {response.text}')
        if max_retry - 1 <= 0:
            return parse_response(response)
        return post_data(url, data, max_retry - 1)
    
    return parse_response(response)


def put_data(url, data={}, max_retry=3):
    """
    PUT request to mail server API
    """
    logger.info(f'[MAIL_SERVER] put_data: {url} - data: {data} - retry: {max_retry}')
    
    try:
        response = httpx.put(
            f"{config.MAIL_SERVER_URL}{url}",
            headers=get_auth_headers(),
            json=data,
            timeout=30.0
        )
    except Exception as e:
        logger.error(f"put_data exception: {e} - retry: {max_retry}")
        if max_retry - 1 <= 0:
            return False, str(e)
        return put_data(url, data, max_retry - 1)

    if response.status_code not in [200, 201]:
        logger.error(f'put_data error: {response.status_code} - {response.text}')
        if max_retry - 1 <= 0:
            return parse_response(response)
        return put_data(url, data, max_retry - 1)
    
    return parse_response(response)


def delete_data(url, max_retry=3):
    """
    DELETE request to mail server API
    """
    logger.info(f'[MAIL_SERVER] delete_data: {url} - retry: {max_retry}')
    
    try:
        response = httpx.delete(
            f"{config.MAIL_SERVER_URL}{url}",
            headers=get_auth_headers(),
            timeout=30.0
        )
    except Exception as e:
        logger.error(f"delete_data exception: {e} - retry: {max_retry}")
        if max_retry - 1 <= 0:
            return False, str(e)
        return delete_data(url, max_retry - 1)

    if response.status_code not in [200, 204]:
        logger.error(f'delete_data error: {response.status_code} - {response.text}')
        if max_retry - 1 <= 0:
            return parse_response(response)
        return delete_data(url, max_retry - 1)
    
    return parse_response(response)


# ============================================
# Mail Server API Functions
# ============================================

def create_mail_user(data):
    """
    Create a new mail user (no authentication required)
    
    Args:
        data (dict): User data containing:
            - username (str): Username for the mail account
            - email (str): User's email address
            - password (str): User's password
            - refId (str): Reference UUID from ProfileHR
            - role (str, optional): User role, defaults to "USER"
            - active (bool, optional): Account active status, defaults to True
    
    Returns:
        tuple: (success: bool, response: dict/str)
    
    Example usage:
        data = {
            "username": "quangnguyen",
            "password": "123456",
            "email": "quangnguyen@gmail.com",
            "role": "USER",
            "active": True,
            "refId": "REF001"
        }
        success, response = create_mail_user(data)
    """
    # Ensure refId is a string if it's a UUID
    if 'refId' in data and not isinstance(data['refId'], str):
        data['refId'] = str(data['refId'])
    
    # Set defaults if not provided
    if 'role' not in data:
        data['role'] = 'USER'
    if 'active' not in data:
        data['active'] = True
    
    # Create user without authentication (public endpoint)
    logger.info(f'[MAIL_SERVER] create_mail_user: {data.get("username")} - {data.get("email")}')
    
    try:
        response = httpx.post(
            f"{config.MAIL_SERVER_URL}/api/users",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=30.0
        )
    except Exception as e:
        logger.error(f"create_mail_user exception: {e}")
        return False, str(e)

    if response.status_code not in [200, 201]:
        logger.error(f'create_mail_user error: {response.status_code} - {response.text}')
        return False, response.text
    
    try:
        result = response.json() if response.text else {}
        return True, result
    except Exception as e:
        logger.error(f"create_mail_user parse error: {e}")
        return True, response.text


def get_mail_user(email):
    """
    Get mail user details
    
    Args:
        email (str): User's email address
    
    Returns:
        dict: User details or None
    """
    return get_data(f"/api/users/{email}")


def list_mail_users():
    """
    List all mail users
    
    Returns:
        list: List of users or empty list
    """
    result = get_data("/api/users")
    return result if result else []


def update_mail_user_password(email, password):
    """
    Update mail user password
    
    Args:
        email (str): User's email address
        password (str): New password
    
    Returns:
        tuple: (success: bool, response: dict/str)
    """
    data = {
        "password": password
    }
    return put_data(f"/api/users/{email}/password", data)


def delete_mail_user(email):
    """
    Delete a mail user
    
    Args:
        email (str): User's email address
    
    Returns:
        tuple: (success: bool, response: dict/str)
    """
    return delete_data(f"/api/users/{email}")
