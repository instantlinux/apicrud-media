"""event models

This is for adding and testing extensions to the core db schema

created 7-sep-2020 by richb@instantlinux.net
"""

from sqlalchemy import Column, Enum, ForeignKey, String, TEXT, TIMESTAMP
from sqlalchemy import func
from sqlalchemy.orm import relationship, backref

from .base import AsDictMixin, Base


class Event(AsDictMixin, Base):
    __tablename__ = 'events'

    id = Column(String(16), primary_key=True, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(TEXT(), nullable=False)
    category_id = Column(ForeignKey(u'categories.id'), nullable=False)
    privacy = Column(String(8), nullable=False, server_default=u'public')
    uid = Column(ForeignKey(u'people.id', ondelete='CASCADE'), nullable=False)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'canceled', u'disabled'),
                    nullable=False)

    category = relationship('Category')
    owner = relationship('Person', foreign_keys=[uid], backref=backref(
        'event_uid', cascade='all, delete-orphan'))
