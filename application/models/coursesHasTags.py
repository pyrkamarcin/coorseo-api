import uuid

from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.dialects.postgresql import UUID

from application.models.users import Users

from application.shared.models import db_session, model


class CoursesHasTags(model):
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
