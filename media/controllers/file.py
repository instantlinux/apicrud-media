"""file.py

File attachments controller

created 14-jan-2020 by richb@instantlinux.net
"""

from apicrud.basic_crud import BasicCRUD
from apicrud.media.storage import StorageAPI
import media_worker


class FileController(BasicCRUD):
    def __init__(self):
        super().__init__(resource="file")

    @staticmethod
    def file_upload_url(body):
        return StorageAPI(credential_ttl=body.get("ttl")).get_upload_url(body)

    @staticmethod
    def upload_complete(id, status):
        return StorageAPI().upload_complete(
                id, status, media_worker.incoming.delay)
