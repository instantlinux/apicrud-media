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
        """Login a new session

        Args:
          body (dict): specify username and password
        Returns:
          dict:
            Fields include jwt_token (contains uid / account ID),
            ID of entry in settings database, and a sub-dictionary
            with mapping of endpoints registered to microservices
        """
        return SessionAuth(config=config, models=models).account_login(
            body['username'], body['password'], roles_from=models.List)

    def logout():
        """Logout

        Returns:
          tuple: dict with message and http status code 200
        """
        return dict(message='logged out'), 200
