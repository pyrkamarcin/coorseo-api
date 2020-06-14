from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

import os

from application.models.agreements import Agreements
from application.models.courses import Courses
from application.models.coursesHasTags import CoursesHasTags
from application.models.keywords import Keywords
from application.models.platforms import Platforms
from application.models.publishers import Publishers
from application.models.ratings import Ratings
from application.models.releases import Releases
from application.models.releaseTypes import ReleaseTypes
from application.models.reviews import Reviews
from application.models.tags import Tags
from application.models.userAgreements import UserAgreements
from application.models.userEvents import UserEvents
from application.models.users import Users

db = SQLAlchemy()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from application.shared.models import model, engine, db_session

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    model.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
