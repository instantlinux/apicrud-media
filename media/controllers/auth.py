"""auth stub for microservice unit-tests

See example/controllers/auth.py in apicrud repo for full implementation
This is temporary, until API-key authentication is added

created 17-may-2020 by richb@instantlinux.net
"""

from apicrud.session_auth import SessionAuth
import config
import models


class AuthController(object):

    def __init__(self):
        self.resource = 'auth'

    @staticmethod
    def login(body):
        return SessionAuth(config=config, models=models).account_login(
            body['username'], body['password'], roles_from=models.List)

    def logout():
        return dict(message='logged out'), 200
