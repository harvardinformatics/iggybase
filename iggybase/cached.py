from flask import current_app, request, g
from functools import wraps

def cached(timeout = (5 *60)):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # exp cache_key: view/59/murray/core/summary/oligo/ajax
            cache_key = 'view/' + str(g.role_id) + request.path
            response = current_app.cache.get(cache_key)
            if not response:
                response = f(*args, **kwargs)
                current_app.cache.set(cache_key, response, timeout)
            return response
        return decorated_function
    return decorator
