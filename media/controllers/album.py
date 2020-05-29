"""album.py

Media album controller

created 14-jan-2020 by richb@instantlinux.net
"""

import logging


from flask import g

from apicrud.basic_crud import BasicCRUD
from apicrud.grants import Grants
from apicrud.media.storage import StorageAPI
import config
import models


class AlbumController(BasicCRUD):
    def __init__(self):
        super().__init__(resource="album", model=models.Album, config=config,
                         models=models)

    @staticmethod
    def create(body):
        """add default value of storage-id, convert sizes to str
        """
        if "sizes" in body:
            res_max = Grants(models, g.db,
                             ttl=config.REDIS_TTL).get("photo_res_max")
            if max(body["sizes"]) > res_max:
                return dict(message="res_max=%d exceeded" % res_max), 405
            if res_max not in body["sizes"]:
                body["sizes"].append(res_max)
            body["sizes"] = ",".join(map(str, sorted(body["sizes"])))
        return super(AlbumController, AlbumController).create(body)

    @staticmethod
    def update(id, body):
        """convert sizes to str
        """
        if "sizes" in body:
            body["sizes"] = ",".join(map(str, sorted(body["sizes"])))
        body.pop("pictures", None)
        # TODO deal with removing/sorting pictures
        return super(AlbumController, AlbumController).update(id, body)

    @staticmethod
    def get(id, details):
        """after fetching, convert sizes to list; build media gallery
        details object if requested
        """
        results, status = super(AlbumController, AlbumController).get(id)
        if status == 200:
            results["sizes"] = [int(x) for x in results["sizes"].split(",")]
            if details:
                results["media"] = StorageAPI(
                    models=models, redis_host=config.REDIS_HOST
                ).fetch_album_meta(id, results["sizes"][0])
        return results, status

    @staticmethod
    def find(**kwargs):
        """after fetching, convert sizes to list
        """
        results, status = super(AlbumController, AlbumController).find(
            **kwargs)
        for record in results["items"]:
            record["sizes"] = [int(x) for x in record["sizes"].split(",")]
        return results, status
