"""main.py

Flask API main entrypoint for media service

created 9-dec-2019 by richb@instantlinux.net
"""

import connexion
from datetime import datetime
from flask import g
import os

import controllers
import db_schema
import models
from apicrud import database, utils
from apicrud.service_config import ServiceConfig
from apicrud.service_registry import ServiceRegistry
from apicrud.session_manager import SessionManager

application = connexion.FlaskApp(__name__)
config = ServiceConfig(reset=True, file=os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'config.yaml'), models=models).config
utils.initialize_app(application)


@application.app.before_first_request
def setup_db(db_url=None, redis_conn=None, migrate=False):
    """Database setup

    Args:
      db_url (str): URL with db host, credentials and db name
      redis_conn (obj): connection to redis
      migrate (bool): perform migrations only if True
    """
    db_url = db_url or config.DB_URL
    ServiceRegistry().register(controllers.resources())
    if __name__ in ['__main__', 'main', 'uwsgi_file_main']:
        database.initialize_db(
            models, db_url=db_url, redis_host=config.REDIS_HOST,
            redis_conn=redis_conn,
            migrate=migrate, geo_support=config.DB_GEO_SUPPORT,
            connection_timeout=config.DB_CONNECTION_TIMEOUT,
            schema_update=db_schema.update,
            schema_maxtime=config.DB_SCHEMA_MAXTIME)


@application.app.before_request
def before_request():
    """Request-setup function - get sessions to database and auth
    """
    g.db = database.get_session()
    g.session = SessionManager()
    g.request_start_time = datetime.utcnow()


@application.app.after_request
def add_header(response):
    """All responses get a cache-control header"""
    response.cache_control.max_age = config.HTTP_RESPONSE_CACHE_MAX_AGE
    return response


@application.app.teardown_appcontext
def cleanup(resp_or_exc):
    """When a flask thread terminates, close the database session"""
    if hasattr(g, 'db'):
        g.db.remove()


if __name__ == '__main__':
    application.run(port=config.APP_PORT)
