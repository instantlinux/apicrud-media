"""file.py

File attachments controller

created 14-jan-2020 by richb@instantlinux.net
"""

from apicrud.basic_crud import BasicCRUD
import config
from apicrud.media.storage import StorageAPI
import media_worker
import models


class FileController(BasicCRUD):
    def __init__(self):
        super().__init__(resource="file", model=models.File, config=config,
                         models=models)

    @staticmethod
    def file_upload_url(body):
        return StorageAPI(
            redis_host=config.REDIS_HOST, redis_port=config.REDIS_PORT,
            models=models, credential_ttl=body.get("ttl")).get_upload_url(body)

    @staticmethod
    def upload_complete(id, status):
        return StorageAPI(
            redis_host=config.REDIS_HOST, redis_port=config.REDIS_PORT,
            models=models).upload_complete(
            id, status, media_worker.incoming.delay)
