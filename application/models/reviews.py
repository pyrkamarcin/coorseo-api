from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from passlib.hash import sha256_crypt
import uuid

from application.models.users import Users
from application.models.courses import Courses


from application.shared.models import db_session, model, engine


class Reviews(model):
    query = db_session.query_property()

    __tablename__ = 'reviews'

    id = Column('review_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    description = Column(String(10000), nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'), nullable=False)
    course = relationship('Courses', backref='reviews', lazy=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    user = relationship('Users', backref="reviews", lazy=True)

    def __init__(self, user: Users, course: Courses, description: str):
        self.user = user
        self.course = course
        self.description = description

    def to_json(self):
        return dict(name=self.description)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)
