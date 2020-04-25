import numpy as np

from flask_marshmallow.fields import Hyperlinks, URLFor
from flask_marshmallow.sqla import SQLAlchemySchema, auto_field, HyperlinkRelated
from marshmallow import fields, pre_load, Schema
from marshmallow.fields import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, json

from passlib.hash import sha256_crypt

import uuid

engine = create_engine('postgresql+psycopg2://user:password@db:5432/coorseo',
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def init_db():
    Model.metadata.create_all(bind=engine)


Model = declarative_base(name='Model')


class Users(Model):
    query = db_session.query_property()

    __tablename__ = 'users'

    id = Column('user_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    email = Column(String(200), unique=True, nullable=False)
    name = Column(String(200), unique=True, nullable=False)
    password = Column(String(100))

    first_name = Column(String(200))
    last_name = Column(String(200))

    confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_on = Column(DateTime, nullable=True)

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = sha256_crypt.encrypt(password)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class UsersSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()


class UserEvents(Model):
    query = db_session.query_property()

    __tablename__ = 'user_events'
    id = Column('user_event_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    log = Column(String(512), unique=False, nullable=False)
    created_on = Column(DateTime, server_default=func.now())

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    user = relationship('Users', backref="user_events", lazy=True)

    def __init__(self, user: Users, log: str):
        self.user = user
        self.log = log

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class UserEventsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()
    log = fields.String()
    user = fields.Nested('UsersSchema', many=False)


class Courses(Model):
    query = db_session.query_property()

    __tablename__ = 'courses'

    id = Column('course_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = Column(String(200), nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    platform_id = Column(UUID(as_uuid=True), ForeignKey('platforms.platform_id'), nullable=False)
    platform = relationship("Platforms", backref=backref("courses", lazy="dynamic"))

    publisher_id = Column(UUID(as_uuid=True), ForeignKey('publishers.publisher_id'), nullable=False)
    publisher = relationship("Publishers", backref=backref("courses", lazy="dynamic"))

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class CoursesSchema(Schema):
    class Meta:
        ordered = True

    def ratings_average_calculate(self, obj):
        point = []
        for rating in obj.ratings:
            point.append(rating.points)
        return np.average(point)

    id = fields.UUID()

    name = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    platform = fields.Nested('PlatformsSchema')
    publisher = fields.Nested('PublishersSchema')

    ratings = fields.Nested('RatingsSchema', many=True)
    ratings_count = fields.Function(lambda obj: len(obj.ratings))
    ratings_average = fields.Method("ratings_average_calculate")

    reviews = fields.Nested('ReviewsSchema', many=True)
    reviews_count = fields.Function(lambda obj: len(obj.reviews))

    _links = Hyperlinks(
        {"self": URLFor("courses.get", id="<id>"), "collection": URLFor("courses.get_all")}
    )


class Platforms(Model):
    query = db_session.query_property()

    __tablename__ = 'platforms'

    id = Column('platform_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = Column(String(200), unique=True, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class PlatformsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    name = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    _links = Hyperlinks(
        {"self": URLFor("platforms.get", id="<id>"), "collection": URLFor("platforms.get_all")}
    )


class Publishers(Model):
    query = db_session.query_property()

    __tablename__ = 'publishers'

    id = Column('publisher_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = Column(String(200), unique=True, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class PublishersSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    name = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    _links = Hyperlinks(
        {"self": URLFor("publishers.get", id="<id>"), "collection": URLFor("publishers.get_all")}
    )


class Ratings(Model):
    query = db_session.query_property()

    __tablename__ = 'ratings'

    id = Column('rating_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    points = Column(Integer, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'), nullable=False)
    course = relationship('Courses', backref='ratings', lazy=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    user = relationship('Users', backref="ratings", lazy=True)

    def __init__(self, user: Users, points: int):
        self.user = user
        self.points = points

    def to_json(self):
        return dict(name=self.points)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class RatingsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    points = fields.Integer()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    user = fields.Nested('UsersSchema', many=False)

    _links = Hyperlinks(
        {"self": URLFor("ratings.get", id="<id>"), "collection": URLFor("ratings.get_all")}
    )


class Reviews(Model):
    query = db_session.query_property()

    __tablename__ = 'reviews'

    id = Column('review_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    description = Column(String(200), nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'), nullable=False)
    course = relationship('Courses', backref='reviews', lazy=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    user = relationship('Users', backref="reviews", lazy=True)

    def __init__(self, user: Users, description: str):
        self.user = user
        self.description = description

    def to_json(self):
        return dict(name=self.description)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class ReviewsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    description = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    user = fields.Nested('UsersSchema', many=False)

    _links = Hyperlinks(
        {"self": URLFor("reviews.get", id="<id>"), "collection": URLFor("reviews.get_all")}
    )


if __name__ == '__main__':
    init_db()
