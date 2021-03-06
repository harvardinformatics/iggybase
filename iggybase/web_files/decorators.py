from flask import current_app, request, g, render_template
from functools import wraps
import logging
import sys
import inspect

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

def templated():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            context = f(*args, **kwargs)
            # TODO: this is getting a bit messy with 404 and 403, clean up
            req_func = []
            if request.endpoint:
                req_func = request.endpoint.split('.')
            always_render = ['forbidden', 'page_not_found']
            # if caller is the endpoint then return response
            if f.__name__ in req_func or f.__name__ in always_render:
                return render_template(context['template'], **context)
            # if not endpoint then return context for further mod, exp workflows
            else:
                return context
        return decorated_function
    return decorator
