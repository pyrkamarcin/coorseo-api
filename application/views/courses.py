import json

from elasticsearch import Elasticsearch
from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt_extended import jwt_required
from flask_uuid import FlaskUUID
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.strategy_options import lazyload, joinedload
import uuid

from application.models.models import Courses, CoursesSchema, db_session, Platforms, Ratings, Keywords, KeywordsSchema

mod = Blueprint(
    'courses',
    __name__,
    url_prefix='/api/courses'
)

es = Elasticsearch(hosts='es01:9200')

course_schema = CoursesSchema()
courses_schema = CoursesSchema(many=True)

keyword_schema = KeywordsSchema()
keyword_schemas = KeywordsSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(courses_schema.dump(Courses.query.options().all()))
    # return jsonify(courses_schema.dump(Courses.query.join(Ratings, isouter=True).group_by(Courses.id).options().all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(course_schema.dump(Courses.query.options().get(id)))
    # return jsonify(course_schema.dump(Courses.query.join(Ratings, isouter=True).options().get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'name' in request.json:
        abort(400)

    name = request.json['name']
    platform_id = request.json['platform']
    publisher_id = request.json['publisher']

    course = Courses(name)
    course.platform_id = platform_id
    course.publisher_id = publisher_id

    db_session.add(course)
    db_session.commit()

    # https://github.com/seek-ai/esengine
    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_schema.dump(course)))

    return course_schema.dump(course)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Courses.query.get(id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:id>', methods=['PUT'])
def update(id):
    course = Courses.query.get(id)
    course.name = request.json.get('name', course.name)
    course.updated_on = func.now()

    db_session.commit()

    # es.update(index='courses', doc_type='title', id=course.id, body=json.dumps(course_schema.dump(course)))

    return jsonify(course_schema.dump(Courses.query.join(Ratings, isouter=True).group_by(Courses.id).get(id)))


@mod.route('/<uuid:course_id>/keywords/', methods=['POST'])
def add_keyword(course_id):
    if not request.json or not 'name' in request.json:
        abort(400)
    course = Courses.query.get(course_id)

    name = request.json['name']
    keyword = Keywords(name)
    course.keywords.append(keyword)

    course.updated_on = func.now()

    db_session.commit()

    # es.update(index='courses', doc_type='title', id=course_id, body=json.dumps(course_schema.dump(course)))

    return keyword_schema.dump(keyword)


@mod.route('/<uuid:course_id>/keywords/<uuid:keyword_id>', methods=['GET'])
def keywords_get(course_id, keyword_id):
    return jsonify(keyword_schema.dump(Keywords.query.options().get(keyword_id)))


@mod.route('/<uuid:course_id>/keywords/', methods=['GET'])
def keywords_get_all(course_id):
    return jsonify(keyword_schemas.dump(Keywords.query.filter_by(course_id=course_id).options().all()))
