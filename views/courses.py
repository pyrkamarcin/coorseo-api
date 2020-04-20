import json

from flask import Blueprint, request, jsonify, abort, make_response
from sqlalchemy import func
from sqlalchemy.orm.strategy_options import lazyload, joinedload

from ..models import Courses, CoursesSchema, db_session, Platforms

mod = Blueprint(
    'courses',
    __name__,
    url_prefix='/api/courses'
)

course_schema = CoursesSchema()
courses_schema = CoursesSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(courses_schema.dump(Courses.query.options().all()))


@mod.route('/<int:id>', methods=['GET'])
def get(id):
    return jsonify(course_schema.dump(Courses.query.options().get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'name' in request.json:
        abort(400)

    name = request.json['name']
    platform_id = request.json['platform_id']
    publisher_id = request.json['publisher_id']

    course = Courses(name)
    course.platform_id = platform_id
    course.publisher_id = publisher_id

    db_session.add(course)
    db_session.commit()
    return course_schema.dump(course)


@mod.route('/<int:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Courses.query.get(id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<int:id>', methods=['PUT'])
def update(id):
    course = Courses.query.get(id)
    course.name = request.json.get('name', course.name)
    course.updated_on = func.now()

    db_session.commit()
    return jsonify(course_schema.dump(Courses.query.get(id)))
