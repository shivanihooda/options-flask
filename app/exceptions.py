# app/exceptions.py


# third party imports
from flask import current_app


class CustomException(Exception):
    """ """

    def __init__(self, message, status_code, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload
        self.log()

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

    def log(self):
        current_app.logger.error(self.message, exc_info=True)


class NoResultFound(CustomException):
    pass


class BadRequest(CustomException):
    pass


class NotAcceptable(CustomException):
    pass