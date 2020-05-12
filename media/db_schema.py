"""db_schema.py

Database schema update and seed functions - populate a new db with minimum data

created 31-mar-2019 by richb@instantlinux.net
"""

import alembic.config
import alembic.script
from alembic.runtime.environment import EnvironmentContext
import logging
import os
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import exc
from sqlalchemy.sql import select, func
import time

from apicrud.database import Base, get_session, spatialite_loaded
from models import AlembicVersion


def update(db_engine, models, migrate=False, schema_maxtime=0,
           script_location=os.path.join(os.path.abspath(
               os.path.dirname(__file__)), 'alembic')):
    """Run alembic migrations for updating schema

    Must be called with mutex for duration of update to prevent race
    conditions; begin_transaction() does not ensure mutual exclusion.

    params:
      models - models to generate or update
      migrate - perform migrations only if True
      schema_maxtime - maximum seconds to wait for mutex
    """
    db_session = get_session(scoped=True)
    try:
        version = db_session.query(AlembicVersion).one().version_num
        if schema_maxtime == 0:
            logging.info('found schema version=%s, skipping update' % version)
            db_session.close()
            return
    except (exc.NoResultFound, OperationalError, ProgrammingError) as ex:
        logging.warning('DB schema does not yet exist: %s' % str(ex))
        version = None

    # TODO move below code into library: it doesn't get called for media
    # anyway; need to create a way for such secondary services to
    # register their endpoints with the primary service (and therefore
    # have a way to validate schema version)

    cfg = alembic.config.Config()
    cfg.set_main_option('script_location', script_location)
    script = alembic.script.ScriptDirectory.from_config(cfg)
    env = EnvironmentContext(cfg, script)
    if (version == script.get_heads()[0]):
        logging.info('action=schema_update version=%s is current' %
                     version)
    elif migrate:
        def _do_upgrade(revision, context):
            return script._upgrade_revs(script.get_heads(), revision)

        conn = db_engine.connect()
        if db_engine.dialect.name == 'sqlite' and spatialite_loaded:
            conn.execute(select([func.InitSpatialMetaData(1)]))
        env.configure(connection=conn, target_metadata=Base.metadata,
                      verbose=True, fn=_do_upgrade)
        with env.begin_transaction():
            env.run_migrations()
        logging.info('action=schema_update finished migration, '
                     'version=%s' % script.get_heads()[0])
    else:
        # Not migrating: must wait
        wait_time = schema_maxtime
        while version != script.get_heads()[0] and wait_time:
            time.sleep(5)
            wait_time -= 5
    if version is None:
        _seed_new_db(db_session)
    db_session.close()


def _seed_new_db(db_session):
    """ Seed a new db - do not execute except in main service
    """

    logging.error('action=seed_new_db message_unsupported')
    raise AssertionError('database unavailable')
