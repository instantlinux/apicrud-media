"""media_worker.py

Celery worker to process media

created 3-feb-2020 by richb@instantlinux.net
"""

import celery
from datetime import datetime
import logging
import os

from apicrud import initialize
from apicrud.exceptions import MediaUploadError
from apicrud.media.worker_processing import MediaProcessing
from apicrud.metrics import Metrics

import celeryconfig
import constants
import models

app = celery.Celery()
app.config_from_object(celeryconfig)


@app.task(name="tasks.media.media_worker.incoming")
def incoming(uid, file_id):
    """Process an incoming media file after it has been stored in
    the cloud bucket.

    Args:
      uid (str): User ID
      file_id (str): ID of file
    """
    start_time = datetime.utcnow()
    media = MediaProcessing(uid, file_id)
    logging.info("action=incoming uid=%s name=%s file_id=%s " % (
        uid, media.meta["name"], file_id))
    if media.meta["ctype"] in constants.MIME_IMAGE_TYPES:
        media.photo(media.meta)
        Metrics().store('photo_processing_seconds_total',
                        value=datetime.utcnow().timestamp() - start_time)
    elif media.meta["ctype"] in constants.MIME_VIDEO_TYPES:
        media.video(media.meta)
        Metrics().store('video_processing_seconds_total',
                        value=datetime.utcnow().timestamp() - start_time)
    else:
        # TODO heic will require another library
        #  https://stackoverflow.com/questions/54395735/how-to-work-with-heic-image-file-types-in-python
        raise MediaUploadError("Unknown type=%s" % media.meta["ctype"])

    logging.info("action=incoming status=success uid=%s name=%s file_id=%s "
                 % (uid, media.meta["name"], file_id))


initialize.worker(models=models,
                  path=os.path.dirname(os.path.abspath(__file__)))
