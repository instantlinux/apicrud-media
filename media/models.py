"""models

Database model definitions for SQLalchemy

created 26-mar-2019 by richb@instantlinux.net

license: lgpl-2.1
"""

# coding: utf-8

import base64
from sqlalchemy import BIGINT, LargeBinary, BOOLEAN, BLOB, Column, Enum, \
     Float, ForeignKey, INTEGER, SMALLINT, String, TEXT, TIMESTAMP, Unicode, \
     UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

import config
import constants

Base = declarative_base()
aes_secret = config.DB_AES_SECRET


class Account(Base):
    __tablename__ = 'accounts'
    __table_args__ = (
        UniqueConstraint(u'id', u'uid', name='uniq_account_user'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(32), nullable=False, unique=True)
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False,
                 unique=True)
    password = Column(EncryptedType(Unicode, aes_secret, AesEngine, 'pkcs5'),
                      nullable=False)
    password_must_change = Column(BOOLEAN, nullable=False,
                                  server_default="False")
    totp_secret = Column(EncryptedType(Unicode, aes_secret, AesEngine,
                                       'pkcs5'))
    is_admin = Column(BOOLEAN, nullable=False, server_default="False")
    settings_id = Column(ForeignKey(u'settings.id'), nullable=False)
    last_login = Column(TIMESTAMP)
    invalid_attempts = Column(INTEGER, nullable=False, server_default="0")
    last_invalid_attempt = Column(TIMESTAMP)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum(u'active', u'disabled'), nullable=False)

    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'account_uid', cascade='all, delete-orphan'))
    settings = relationship('Settings')

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns
                if col.name not in [
                        'password', 'totp_secret', 'invalid_attempts',
                        'last_invalid_attempt']}


class Album(Base):
    __tablename__ = 'albums'
    __table_args__ = (
        UniqueConstraint(u'name', u'uid', name='uniq_album_user'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    sizes = Column(String(32), nullable=False,
                   server_default=constants.DEFAULT_THUMBNAIL_SIZES)
    encryption = Column(Enum(u'aes'))
    password = Column(EncryptedType(Unicode, aes_secret, AesEngine, 'pkcs5'))
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False)
    list_id = Column(ForeignKey(u'lists.id'))
    cover_id = Column(ForeignKey(u'pictures.id'))
    category_id = Column(ForeignKey(u'categories.id'), nullable=False)
    privacy = Column(String(8), nullable=False, server_default=u'invitee')
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    pictures = relationship('Picture', secondary='albumcontents',
                            backref=backref('albums'),
                            order_by='AlbumContent.rank')
    cover = relationship('Picture', foreign_keys=[cover_id])
    list = relationship('List')
    category = relationship('Category')
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'album_uid', cascade='all, delete-orphan'))

    def as_dict(self):
        retval = {col.name: getattr(self, col.name)
                  for col in self.__table__.columns}
        retval['pictures'] = [picture.id for picture in self.pictures]
        return retval


class AlbumContent(Base):
    __tablename__ = 'albumcontents'
    __table_args__ = (
        UniqueConstraint(u'album_id', u'picture_id', name='uniq_albumpic'),
    )

    album_id = Column(ForeignKey(u'albums.id', ondelete='CASCADE'),
                      primary_key=True, nullable=False)
    picture_id = Column(ForeignKey(u'pictures.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    rank = Column(Float)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())

    album = relationship('Album', foreign_keys=[album_id], backref=backref(
        'albumcontents', cascade='all, delete-orphan'))
    picture = relationship('Picture', backref=backref(
        'albumcontents', cascade='all, delete-orphan'))


class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        UniqueConstraint(u'name', u'uid', name='uniq_category_owner'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    uid = Column(ForeignKey(u'people.id'), nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'category_uid', cascade='all, delete-orphan'))

    # TODO - dry this out
    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = (
        UniqueConstraint(u'info', u'type', name='uniq_info_type'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    label = Column(Enum(u'home', u'mobile', u'other', u'work'),
                   nullable=False, server_default=u'home')
    type = Column(Enum(u'email', u'linkedin', u'location', u'messenger',
                       u'slack', u'sms', u'voice', u'whatsapp'),
                  nullable=False, server_default=u'email')
    carrier = Column(String(16))
    info = Column(String(255))
    muted = Column(BOOLEAN, nullable=False, server_default="False")
    rank = Column(INTEGER, nullable=False, server_default="1")
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False,
                 index=True)
    privacy = Column(String(8), nullable=False, server_default=u'member')
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum(u'active', u'unconfirmed', u'disabled'),
                    nullable=False, server_default=u'unconfirmed')

    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'contacts', cascade='all, delete-orphan'))

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class Credential(Base):
    __tablename__ = 'credentials'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    vendor = Column(String(32), nullable=False)
    # placeholder field TODO make clear how this will be used
    #  probably to delegate to Secrets Manager / KMS
    type = Column(String(16))
    url = Column(String(length=64))
    key = Column(String(length=128))
    secret = Column(EncryptedType(Unicode, aes_secret, AesEngine, 'pkcs5'))
    otherdata = Column(EncryptedType(Unicode, aes_secret, AesEngine, 'pkcs5'))
    expires = Column(TIMESTAMP)
    settings_id = Column(ForeignKey(u'settings.id'), nullable=False)
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum(u'active', u'disabled'), nullable=False,
                    server_default=u'active')

    settings = relationship('Settings', foreign_keys=[settings_id])
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'credential_uid', cascade='all, delete-orphan'))

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class File(Base):
    __tablename__ = 'files'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    path = Column(String(64), nullable=False)
    mime_type = Column(String(32), nullable=False, server_default="text/plain")
    size = Column(BIGINT)
    sha1 = Column(LargeBinary(length=20))
    sha256 = Column(LargeBinary(length=32))
    storage_id = Column(ForeignKey(u'storageitems.id'))
    list_id = Column(ForeignKey(u'list.id'))
    privacy = Column(String(8), nullable=False, server_default=u'member')
    uid = Column(ForeignKey(u'people.id'), nullable=False, index=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    storage = relationship('Storage')
    # TODO
    # list = relationship('List')

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class Grant(Base):
    __tablename__ = 'grants'
    __table_args__ = (
        UniqueConstraint(u'name', u'uid', name='uniq_grant_user'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(24), nullable=False)
    value = Column(String(64), nullable=False)
    uid = Column(ForeignKey(u'people.id'), nullable=False)
    expires = Column(TIMESTAMP)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'grant_uid', cascade='all, delete-orphan'))

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class List(Base):
    __tablename__ = 'lists'
    __table_args__ = (
        UniqueConstraint(u'name', u'uid', name='uniq_list_owner'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    description = Column(TEXT())
    privacy = Column(String(8), nullable=False, server_default=u'secret')
    category_id = Column(ForeignKey(u'categories.id'), nullable=False)
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False)

    album = relationship('Album')
    files = relationship('File', secondary='listfiles',
                         backref=backref('files'))
    category = relationship('Category')
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'list_uid', cascade='all, delete-orphan'))

    def as_dict(self):
        retval = self.__dict__.copy()
        retval['members'] = [member.id for member in self.members]
        retval.pop('_sa_instance_state', None)
        return retval


# see https://docs.sqlalchemy.org/en/13/orm/extensions/associationproxy.html
class ListFile(Base):
    __tablename__ = 'listfiles'
    __table_args__ = (
        UniqueConstraint(u'list_id', u'file_id', name='uniq_listfile'),
    )

    file_id = Column(ForeignKey(u'files.id', ondelete='CASCADE'),
                     primary_key=True, nullable=False)
    list_id = Column(ForeignKey(u'lists.id', ondelete='CASCADE'),
                     nullable=False, index=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())

    file = relationship('File', foreign_keys=[file_id], backref=backref(
        'listfiles', cascade='all, delete-orphan'))
    list = relationship('List', backref=backref(
        'listfiles', cascade='all, delete-orphan'))


class Message(Base):
    __tablename__ = 'messages'

    id = Column(String(16), primary_key=True, unique=True)
    content = Column(TEXT(), nullable=False)
    subject = Column(String(128))
    sender_id = Column(ForeignKey(u'people.id'), nullable=False)
    recipient_id = Column(ForeignKey(u'people.id'))
    # TODO use the many-to-many table instead
    list_id = Column(ForeignKey(u'lists.id'))
    privacy = Column(String(8), nullable=False, server_default=u'secret')
    published = Column(BOOLEAN)
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False)
    viewed = Column(TIMESTAMP)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    list = relationship('List')
    owner = relationship('Person', foreign_keys=[uid])
    recipient = relationship('Person', foreign_keys=[recipient_id])

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


# Message attachments
class MessageFile(Base):
    __tablename__ = 'messagefiles'
    __table_args__ = (
        UniqueConstraint(u'message_id', u'file_id', name='uniq_messagefile'),
    )

    file_id = Column(ForeignKey(u'files.id', ondelete='CASCADE'),
                     primary_key=True, nullable=False)
    message_id = Column(ForeignKey(u'messages.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())

    file = relationship('File', foreign_keys=[file_id], backref=backref(
        'messagefiles', cascade='all, delete-orphan'))
    message = relationship('Message', backref=backref(
        'messagefiles', cascade='all, delete-orphan'))


class Person(Base):
    __tablename__ = 'people'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    identity = Column(String(64), nullable=False, unique=True)
    referrer_id = Column(ForeignKey(u'people.id'))
    privacy = Column(String(8), nullable=False, server_default=u'public')
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled', u'suspended'), nullable=False)

    def as_dict(self):
        retval = {col.name: getattr(self, col.name)
                  for col in self.__table__.columns}
        retval['lists'] = [list.id for list in self.lists]
        return retval


class Picture(Base):
    __tablename__ = 'pictures'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    path = Column(String(64), server_default="", nullable=False)
    caption = Column(String(255))
    uid = Column(ForeignKey(u'people.id'), nullable=False)
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
    category_id = Column(ForeignKey(u'categories.id'), nullable=False)
    storage_id = Column(ForeignKey(u'storageitems.id'), nullable=False)
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


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(32), nullable=False)
    privacy = Column(String(8), nullable=False, server_default=u'public')
    smtp_port = Column(INTEGER, nullable=False, server_default='25')
    smtp_smarthost = Column(String(255))
    smtp_credential_id = Column(ForeignKey(u'credentials.id'))
    country = Column(String(2), nullable=False,
                     server_default=constants.DEFAULT_COUNTRY)
    default_storage_id = Column(ForeignKey(u'storageitems.id'))
    lang = Column(String(6), nullable=False,
                  server_default=constants.DEFAULT_LANG)
    tz_id = Column(ForeignKey(u'time_zone_name.id'), nullable=False,
                   server_default='598')
    url = Column(String(255))
    # theme_id = Column(ForeignKey(u'themes.id'), nullable=False)
    window_title = Column(String(127),
                          server_default=constants.WINDOW_TITLE)
    default_cat_id = Column(ForeignKey(u'categories.id'), nullable=False)
    administrator_id = Column(ForeignKey(u'people.id'), nullable=False)
    default_hostlist_id = Column(ForeignKey(u'lists.id'))
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)

    default_category = relationship('Category', foreign_keys=[default_cat_id])
    administrator = relationship('Person')
    default_hostlist = relationship('List',
                                    foreign_keys=[default_hostlist_id])
    tz = relationship('TZname')

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class Storage(Base):
    __tablename__ = 'storageitems'
    __table_args__ = (
        UniqueConstraint(u'name', u'uid', name='uniq_storage_user'),
    )

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(32), nullable=False)
    prefix = Column(String(128))
    bucket = Column(String(64), nullable=False)
    region = Column(String(16),
                    server_default=constants.DEFAULT_AWS_REGION)
    cdn_uri = Column(String(64))
    identifier = Column(String(64))
    privacy = Column(String(8), nullable=False, server_default=u'public')
    credentials_id = Column(ForeignKey(u'credentials.id'))
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default="active")

    credentials = relationship('Credential')
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'storage_uid', cascade='all, delete-orphan'))

    def as_dict(self):
        return {col.name: getattr(self, col.name)
                for col in self.__table__.columns}


class TZname(Base):
    __tablename__ = 'time_zone_name'

    id = Column(INTEGER, primary_key=True, unique=True)
    name = Column(String(32), nullable=False, unique=True)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default="active")


class AlembicVersion(Base):
    __tablename__ = 'alembic_version'

    version_num = Column(String(32), primary_key=True, nullable=False)
