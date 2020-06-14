from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from passlib.hash import sha256_crypt
import uuid

import numpy as np

from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
    ForeignKey, func, Boolean, JSON
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID

from application.models.users import Users

import uuid


class ReviewsSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    description = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    user = fields.Nested('UsersSchema', many=False)

    _links = Hyperlinks(
        {"self": URLFor("courses.reviews_get", course_id="<course_id>", review_id="<id>"),
         "collection": URLFor("courses.reviews_get_all", course_id="<course_id>")}
    )