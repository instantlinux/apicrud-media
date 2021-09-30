"""message models

This is for adding and testing extensions to the core db schema

created 7-sep-2020 by richb@instantlinux.net
"""

from sqlalchemy import BOOLEAN, Column, Enum, ForeignKey, String, TEXT, \
    TIMESTAMP
from sqlalchemy import func
from sqlalchemy.orm import relationship

from apicrud.models.base import AsDictMixin, Base
app_schema = 'media'
schema_pre = app_schema + '.' if app_schema else ''
core_pre = 'apicrud.' if app_schema else ''


class Message(AsDictMixin, Base):
    __tablename__ = 'messages'
    __table_args__ = (
        dict(schema=app_schema),
    )

    id = Column(String(16), primary_key=True, unique=True)
    content = Column(TEXT(), nullable=False)
    subject = Column(String(128))
    sender_id = Column(ForeignKey(u'%speople.id' % core_pre), nullable=False)
    recipient_id = Column(ForeignKey(u'%speople.id' % core_pre))
    # TODO use the many-to-many table instead
    list_id = Column(ForeignKey(u'%slists.id' % core_pre))
    privacy = Column(String(8), nullable=False, server_default=u'secret')
    published = Column(BOOLEAN)
    uid = Column(ForeignKey(u'%speople.id' % core_pre, ondelete='CASCADE'),
                 nullable=False)
    viewed = Column(TIMESTAMP)
    created = Column(TIMESTAMP, nullable=False, server_default=func.now())
    modified = Column(TIMESTAMP)
    status = Column(Enum('active', u'disabled'), nullable=False,
                    server_default=u'active')

    list = relationship('List')
    owner = relationship('Person', foreign_keys=[uid])
    recipient = relationship('Person', foreign_keys=[recipient_id])
