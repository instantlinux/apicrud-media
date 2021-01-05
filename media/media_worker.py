"""media_worker.py

Celery worker to process media

created 3-feb-2020 by richb@instantlinux.net
"""

import celery
import logging
import os

from apicrud import ServiceConfig, database
from apicrud.media.worker_processing import MediaProcessing, \
    MediaUploadException

import celeryconfig
import constants
import models

app = celery.Celery()
app.config_from_object(celeryconfig)
config = ServiceConfig(reset=True, file=os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'config.yaml'), models=models).config


@app.task(name="tasks.media.media_worker.incoming")
def incoming(uid, file_id):
    """Process an incoming media file after it has been stored in
    the cloud bucket.

    Args:
      uid (str): User ID
      file_id (str): ID of file
    """
    db_session = database.get_session(scopefunc=celery.utils.threads.get_ident,
                                      db_url=config.DB_URL)
    media = MediaProcessing(uid, file_id, db_session=db_session)
    logging.info("action=incoming uid=%s name=%s file_id=%s " % (
        uid, media.meta["name"], file_id))
    if media.meta["ctype"] in constants.MIME_IMAGE_TYPES:
        media.photo(uid, media.meta)
    elif media.meta["ctype"] in constants.MIME_VIDEO_TYPES:
        media.video(uid, media.meta)
    else:
        # TODO heic will require another library
        #  https://stackoverflow.com/questions/54395735/how-to-work-with-heic-image-file-types-in-python
        raise MediaUploadException("Unknown type=%s" % media.meta["ctype"])

    logging.info("action=incoming status=success uid=%s name=%s file_id=%s "
                 % (uid, media.meta["name"], file_id))
