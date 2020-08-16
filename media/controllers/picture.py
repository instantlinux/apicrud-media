"""picture.py

Pictures controller

created 14-jan-2020 by richb@instantlinux.net
"""

from flask import g
from sqlalchemy import func

from apicrud.access import AccessControl
from apicrud.account_settings import AccountSettings
from apicrud.basic_crud import BasicCRUD

from models import Album, AlbumContent


class PictureController(BasicCRUD):
    def __init__(self):
        super().__init__(resource="picture")

    @staticmethod
    def create(body):
        """get default storage volume, and append to album if specified
        """

        def _get_count(query):
            count_q = query.statement.with_only_columns([func.count()]
                                                        ).order_by(None)
            return query.session.execute(count_q).scalar()

        account_id = AccessControl().account_id
        if not body.get("storage_id"):
            body["storage_id"] = AccountSettings(
                account_id, g.db).get.default_storage_id
        if not body.get("is_encrypted"):
            # TODO why do I need to set an explicit default value here
            body["is_encrypted"] = False
        album_id = body.get("album_id")
        rank = body.get("rank")
        body.pop("album_id", None)
        body.pop("rank", None)
        retval = super(PictureController, PictureController).create(body)
        if retval[1] == 201 and album_id:
            picture_id = retval[0]["id"]
            count = _get_count(g.db.query(AlbumContent).filter_by(
                album_id=album_id))
            g.db.add(AlbumContent(
                album_id=album_id, picture_id=picture_id,
                rank=rank or count + 1))
            if count == 0:
                album = g.db.query(Album).filter_by(id=album_id).one()
                album.cover_id = picture_id
                g.db.add(album)
            g.db.commit()
        return retval

    @staticmethod
    def update(id, body):
        """handle album_id
        """
        album_id = body.pop("album_id", None)
        rank = body.pop("rank", None)
        retval = super(PictureController, PictureController).update(id, body)
        if retval[1] == 201 and album_id and rank:
            record = g.db.query(AlbumContent).filter(
                AlbumContent.album_id == album_id,
                AlbumContent.picture_id == id).one()
            record.rank = rank
            g.db.commit()
        return retval
