from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

import uuid
from passlib.hash import sha256_crypt

from application.models.releaseTypes import ReleaseTypes


from application.shared.models import db_session, model, engine


class Releases(model):
    query = db_session.query_property()

    __tablename__ = 'releases'

    id = Column('release_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'), nullable=False)
    course = relationship('Courses', backref='releases', lazy=True)

    release_type_id = Column(UUID(as_uuid=True), ForeignKey('release_types.release_type_id'), nullable=False)
    release_type = relationship("ReleaseTypes", backref=backref("release", lazy="dynamic"))

    def __init__(self, name: str, description: str, release_type: ReleaseTypes):
        self.name = name
        self.description = description
        self.release_type = release_type

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)
