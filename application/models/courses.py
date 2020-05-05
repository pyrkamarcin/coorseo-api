import uuid

from sqlalchemy import Column, String, DateTime, \
    ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID

from application.models.users import Users
from application.models.coursesHasTags import CoursesHasTags

from application.shared.models import db_session, model


class Courses(model):
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
