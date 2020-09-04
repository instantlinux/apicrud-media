"""album.py

Media album controller

created 14-jan-2020 by richb@instantlinux.net
"""

from flask import g
from flask_babel import _

from apicrud import BasicCRUD, Grants
from apicrud.media.storage import StorageAPI


class AlbumController(BasicCRUD):
    def __init__(self):
        super().__init__(resource="album")

    @staticmethod
    def create(body):
        """add default value of storage-id, convert sizes to str
        """
        if "sizes" in body:
            res_max = Grants(db_session=g.db).get("photo_res_max")
            if max(body["sizes"]) > res_max:
                return dict(message=_(
                    u"Maximum resolution (%d) exceeded" % res_max)), 405
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
                results["media"] = StorageAPI().fetch_album_meta(
                    id, results["sizes"][0])
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
