import functools

from flask import request, abort

token = open('config/.token', 'r').read().strip()

def requires_token(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        if request.authorization is not None and request.authorization.token == token:
            return await f(*args, **kwargs)
        else:
            abort(401)
    
    return wrapper