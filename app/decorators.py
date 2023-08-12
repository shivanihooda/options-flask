# app/decorators.py


# core imports
from functools import wraps


# third party imports
from flask import jsonify, Response


def to_json(status_code):
    # ToDo: Logging every request as it gets processed
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            resp = func(*args, **kwargs)
            if not isinstance(resp, Response):
                resp = jsonify(resp)
            # finally set the status code
            resp.status_code = status_code
            return resp
        return inner
    return outer

