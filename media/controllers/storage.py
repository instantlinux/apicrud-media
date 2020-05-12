"""storage.py

Storage volumes controller

created 14-jan-2020 by richb@instantlinux.net
"""

from flask import g

from apicrud.access import AccessControl
from apicrud.basic_crud import BasicCRUD
import config
import models


class StorageController(BasicCRUD):
    def __init__(self):
        super().__init__(resource="storage", model=models.Storage,
                         config=config, models=models)

    @staticmethod
    def create(body):
        """after create, set default storage volume if none existed before
        """
        result, status = super(StorageController, StorageController).create(
            body)
        if status == 201:
            record = g.db.query(models.Settings).join(models.Account).filter(
                models.Account.id == AccessControl().account_id).one()
            if not record.default_storage_id:
                record.default_storage_id = result['id']
                g.db.add(record)
                g.db.commit()
        return result, status
