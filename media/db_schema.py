"""db_schema.py

Database schema update and seed functions - populate a new db with minimum data

created 31-mar-2019 by richb@instantlinux.net
"""

import logging
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import exc

from apicrud.database import get_session
from models import AlembicVersion


def update(db_engine, models, migrate=False, schema_maxtime=0):
    """Run alembic migrations for updating schema

    See the example/db_schema.py in main apicrud repo for full
    implementation; microservices do not update schema

    Args:
      db_engine (obj): connection to database
      models (obj): models to generate or update
      migrate (bool): perform migrations only if True
      schema_maxtime (int):  maximum seconds to wait for mutex
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

    # DB schema is maintained by main API: abort if update didn't
    #  take place
    logging.error('action=update message="schema unavailable"')
    raise AssertionError('schema unavailable')
