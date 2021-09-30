"""media models

Database model definitions for SQLalchemy

created 15-may-2020 by richb@instantlinux.net

license: lgpl-2.1
"""

# coding: utf-8

import base64
from sqlalchemy import BIGINT, LargeBinary, BOOLEAN, BLOB, Column, Enum, \
     Float, ForeignKey, INTEGER, SMALLINT, String, TIMESTAMP, Unicode, \
     UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine, \
    StringEncryptedType

import constants
from apicrud.models.base import get_aes_secret, AsDictMixin, Base
app_schema = 'media'
schema_pre = app_schema + '.' if app_schema else ''
core_pre = 'apicrud.' if app_schema else ''


class Album(AsDictMixin, Base):
    __tablename__ = 'albums'
    __table_args__ = (
        UniqueConstraint(u'name', u'uid', name='uniq_album_user'),
        dict(schema=app_schema),
    )
    __rest_related__ = ('pictures',)

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    sizes = Column(String(32), nullable=False,
                   server_default=constants.DEFAULT_THUMBNAIL_SIZES)
    encryption = Column(Enum(u'aes'))
    password = Column(StringEncryptedType(Unicode, get_aes_secret, AesEngine,
                                          'pkcs5', length=64))
    uid = Column(ForeignKey(u'%speople.id' % core_pre, ondelete='CASCADE'),
                 nullable=False)
    list_id = Column(ForeignKey(u'%slists.id' % core_pre))
    event_id = Column(String(16))
    cover_id = Column(ForeignKey(u'%spictures.id' % schema_pre))
    category_id = Column(ForeignKey(u'%scategories.id' % core_pre),
                         nullable=False)
    privacy = Column(String(8), nullable=False, server_default=u'invitee')
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    pictures = relationship('Picture',
                            secondary='%salbumcontents' % schema_pre,
                            backref=backref('albums'),
                            order_by='AlbumContent.rank')
    cover = relationship('Picture', foreign_keys=[cover_id])
    list = relationship('List')
    category = relationship('Category')
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'album_uid', cascade='all, delete-orphan'))


class AlbumContent(Base):
    __tablename__ = 'albumcontents'
    __table_args__ = (
        UniqueConstraint(u'album_id', u'picture_id', name='uniq_albumpic'),
        dict(schema=app_schema),
    )

    album_id = Column(
        ForeignKey(u'%salbums.id' % schema_pre, ondelete='CASCADE'),
        primary_key=True, nullable=False)
    picture_id = Column(
        ForeignKey(u'%spictures.id' % schema_pre, ondelete='CASCADE'),
        nullable=False, index=True)
    rank = Column(Float)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())


class File(AsDictMixin, Base):
    __tablename__ = 'files'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    path = Column(String(64), nullable=False)
    mime_type = Column(String(32), nullable=False, server_default="text/plain")
    size = Column(BIGINT)
    sha1 = Column(LargeBinary(length=20))
    sha256 = Column(LargeBinary(length=32))
    storage_id = Column(ForeignKey(u'%sstorageitems.id' % core_pre))
    list_id = Column(ForeignKey(u'%slist.id' % core_pre))
    event_id = Column(String(16))
    privacy = Column(String(8), nullable=False, server_default=u'member')
    uid = Column(ForeignKey(u'%speople.id' % core_pre), nullable=False,
                 index=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    storage = relationship('Storage')
    # TODO
    # list = relationship('List')


# see https://docs.sqlalchemy.org/en/13/orm/extensions/associationproxy.html
class ListFile(Base):
    __tablename__ = 'listfiles'
    __table_args__ = (
        UniqueConstraint(u'list_id', u'file_id', name='uniq_listfile'),
        dict(schema=app_schema),
    )

    file_id = Column(
        ForeignKey(u'%sfiles.id' % schema_pre, ondelete='CASCADE'),
        primary_key=True, nullable=False)
    list_id = Column(ForeignKey(u'%slists.id' % core_pre, ondelete='CASCADE'),
                     nullable=False, index=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())


# Message attachments
class MessageFile(Base):
    __tablename__ = 'messagefiles'
    __table_args__ = (
        UniqueConstraint(u'message_id', u'file_id', name='uniq_messagefile'),
        dict(schema=app_schema),
    )

    file_id = Column(
        ForeignKey(u'%sfiles.id' % schema_pre, ondelete='CASCADE'),
        primary_key=True, nullable=False)
    message_id = Column(
        ForeignKey(u'%smessages.id' % core_pre, ondelete='CASCADE'),
        nullable=False, index=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())


class Picture(Base):
    __tablename__ = 'pictures'
    __table_args__ = (
        dict(schema=app_schema),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    path = Column(String(64), server_default="", nullable=False)
    caption = Column(String(255))
    uid = Column(ForeignKey(u'%speople.id' % core_pre), nullable=False)
    size = Column(BIGINT)
    sha1 = Column(LargeBinary(length=20))
    sha256 = Column(LargeBinary(length=32))
    thumbnail50x50 = Column(BLOB)
    format_original = Column(Enum(
        'gif', 'heic', 'heif', 'ico', 'jpeg', 'mov', 'mp4', 'png', 'wmv'))
    is_encrypted = Column(BOOLEAN, nullable=False, server_default="False")
    duration = Column(Float)
    # selected EXIF fields
    compression = Column(String(16))
    datetime_original = Column(TIMESTAMP)
    gps_altitude = Column(Float)
    geolat = Column(INTEGER)
    geolong = Column(INTEGER)
    height = Column(INTEGER)
    make = Column(String(16))
    model = Column(String(32))
    orientation = Column(SMALLINT)
    #   Enum(u'Horizontal', u'Mirrored-h', u'Rotated-180',
    #        u'Mirrored-v', u'Mirrored-h-rot-270',
    #        u'Rotated-90', u'Mirrored-h-rot-90', u'Rotated-270')
    width = Column(INTEGER)

    privacy = Column(String(8), nullable=False, server_default=u'invitee')
    category_id = Column(ForeignKey(u'%scategories.id' % core_pre),
                         nullable=False)
    storage_id = Column(ForeignKey(u'%sstorageitems.id' % core_pre),
                        nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False)

    geo = [geolong / 1.0e7, geolat / 1.0e7]
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'picture_uid', cascade='all, delete-orphan'))
    storage = relationship('Storage')
    category = relationship('Category')

    def as_dict(self):
        retval = {col.name: getattr(self, col.name)
                  for col in self.__table__.columns}
        if retval.get('sha1'):
            retval['sha1'] = retval['sha1'].hex()
        if retval.get('sha256'):
            retval['sha256'] = retval['sha256'].hex()
        if retval.get('thumbnail50x50'):
            retval['thumbnail50x50'] = (
                'data:image/%s;base64,' % retval['format_original'] +
                base64.b64encode(retval['thumbnail50x50']).decode('ascii'))
        return retval
