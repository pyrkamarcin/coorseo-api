import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from application.models.users import Users

from application.shared.models import db_session, model


class Keywords(model):
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
