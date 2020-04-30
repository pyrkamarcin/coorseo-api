import numpy as np
from flask import current_app

from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean, JSON, Table
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from passlib.hash import sha256_crypt

import uuid

engine = create_engine("postgresql+psycopg2://user:password@db:5432/coorseo", convert_unicode=True)
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

    created_on = Column(DateTime, server_default=func.now())

    confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_on = Column(DateTime, nullable=True)

    tags = relationship("Agreements", secondary="user_agreements")

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
    meta = Column(JSON, nullable=True)
    created_on = Column(DateTime, server_default=func.now())

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    user = relationship('Users', backref="user_events", lazy=True)

    def __init__(self, user: Users, log: str, meta=None):
        if meta is None:
            meta = {}
        self.user = user
        self.log = log
        self.meta = meta

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

    tags = relationship("Tags", secondary="courses_tags")

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class CoursesSchema(Schema):
    class Meta:
        ordered = True

    @staticmethod
    def ratings_average_calculate(obj):
        point = []
        for rating in obj.ratings:
            point.append(rating.points)
        return np.average(point)

    id = fields.UUID()

    name = fields.String()
    # https://stackoverflow.com/questions/53606872/datetime-format-in-flask-marshmallow-schema
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    platform = fields.Nested('PlatformsSchema')
    publisher = fields.Nested('PublishersSchema')

    ratings = fields.Nested('RatingsSchema', many=True)
    ratings_count = fields.Function(lambda obj: len(obj.ratings))

    reviews = fields.Nested('ReviewsSchema', many=True)
    reviews_count = fields.Function(lambda obj: len(obj.reviews))

    tags = fields.Nested('TagsSchema', many=True)
    keywords = fields.Nested('KeywordsSchema', many=True)

    _links = Hyperlinks(
        {"self": URLFor("courses.get", id="<id>"), "collection": URLFor("courses.get_all")}
    )


class CoursesSearchSchema(Schema):
    class Meta:
        ordered = True

    @staticmethod
    def ratings_average_calculate(obj):
        point = []
        for rating in obj.ratings:
            point.append(rating.points)
        return np.average(point)

    id = fields.UUID()

    name = fields.String()
    # https://stackoverflow.com/questions/53606872/datetime-format-in-flask-marshmallow-schema
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    platform = fields.Nested('PlatformsSchema', only=["name"])
    publisher = fields.Nested('PublishersSchema', only=["name"])

    ratings = fields.Nested('RatingsSchema', many=True)
    ratings_count = fields.Function(lambda obj: len(obj.ratings))

    reviews = fields.Nested('ReviewsSchema', many=True)
    reviews_count = fields.Function(lambda obj: len(obj.reviews))

    tags = fields.Nested('TagsSchema', many=True, only=['name'])
    keywords = fields.Nested('KeywordsSchema', many=True)


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


class Tags(Model):
    query = db_session.query_property()

    __tablename__ = 'tags'

    id = Column('tag_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(2000), nullable=True)

    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def to_json(self):
        return dict(name=self.name, description=self.description)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class TagsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    name = fields.String()
    description = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    _links = Hyperlinks(
        {"self": URLFor("tags.get", id="<id>"), "collection": URLFor("tags.get_all")}
    )


class CoursesHasTags(Model):
    query = db_session.query_property()

    __tablename__ = 'courses_tags'

    id = Column('courses_tags_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True,
                nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('tags.tag_id'), unique=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'), unique=False)

    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    course = relationship("Courses", backref="tags_courses_tags")
    tag = relationship("Tags", backref="courses_courses_tags")


class Keywords(Model):
    query = db_session.query_property()

    __tablename__ = 'keywords'

    id = Column('keyword_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    name = Column(String(200), nullable=False)

    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.course_id'), nullable=False)
    course = relationship('Courses', backref='keywords', lazy=True)

    def __init__(self, name: str):
        self.name = name

    def to_json(self):
        return dict(name=self.name)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class KeywordsSchema(Schema):
    class Meta(Schema.Meta):
        ordered = True

    id = fields.UUID()

    name = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()


class Agreements(Model):
    query = db_session.query_property()

    __tablename__ = 'agreements'

    id = Column('agreement_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(String(200), nullable=True)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    def __init__(self, title: str):
        self.title = title

    def to_json(self):
        return dict(name=self.description)

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class AgreementsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    title = fields.String()
    description = fields.String()
    valid_from = fields.DateTime()
    valid_to = fields.DateTime()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()


class UserAgreements(Model):
    query = db_session.query_property()

    __tablename__ = 'user_agreements'

    id = Column('user_agreements_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True,
                nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), unique=False)
    agreements_id = Column(UUID(as_uuid=True), ForeignKey('agreements.agreement_id'), unique=False)

    is_read = Column(Boolean, default=False)
    is_accepted = Column(Boolean, default=False)

    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    user = relationship("Users", backref="agreements_user_agreements")
    agreement = relationship("Agreements", backref="users_user_agreements")


if __name__ == '__main__':
    init_db()
