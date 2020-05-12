"""main.py

Flask API main entrypoint for media service

created 9-dec-2019 by richb@instantlinux.net
"""

import connexion
from datetime import datetime
from flask import g
import logging

import config
from controllers import _init
import db_schema
import models
from apicrud import database, utils
from apicrud.service_registry import ServiceRegistry
from apicrud.session_manager import SessionManager

application = connexion.FlaskApp(__name__)
utils.initialize_app(application, config, models)
resources = _init.controllers()


@application.app.before_first_request
def setup_db(db_url=config.DB_URL, redis_conn=None, migrate=False,
             schema_update=db_schema.update):
    ServiceRegistry(config).register(resources)
    if __name__ in ['__main__', 'main', 'uwsgi_file_media_main']:
        # TODO remove
        logging.info(dict(action='setup_db', db_url=db_url,
                          redis_host=config.REDIS_HOST,
                          schema_maxtime=config.DB_SCHEMA_MAXTIME))
        database.initialize_db(
            models, db_url=db_url, redis_host=config.REDIS_HOST,
            redis_conn=redis_conn,
            geo_support=config.DB_GEO_SUPPORT,
            connection_timeout=config.DB_CONNECTION_TIMEOUT,
            schema_update=schema_update, migrate=migrate,
            schema_maxtime=config.DB_SCHEMA_MAXTIME)


@application.app.before_request
def before_request():
    g.db = database.get_session()
    # TODO for unittest
    # g.session = SessionManager(config, redis_conn=config.redis_conn)
    g.session = SessionManager(config)
    g.request_start_time = datetime.utcnow()


@application.app.after_request
def add_header(response):
    response.cache_control.max_age = config.HTTP_RESPONSE_CACHE_MAX_AGE
    return response


@application.app.teardown_appcontext
def cleanup(resp_or_exc):
    g.db.remove()


if __name__ == '__main__':
    application.run(port=config.PORT)
