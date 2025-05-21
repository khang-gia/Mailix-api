from django.core.cache import cache
import random
import string

def generate_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generate(email):
    code = generate_string()
    cache.set(email, code, timeout=60*5)
    print('cache', cache.get(email))
    return code

def verify(code, email):
    _c = cache.get(email)
    print('_c', _c)
    if not _c:
        return False
    return _c == code
    