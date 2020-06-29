import json, os

from elasticsearch import Elasticsearch
from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_uuid import FlaskUUID
from sqlalchemy import func
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.strategy_options import lazyload, joinedload
import uuid

from application.shared.models import db_session

from application.models.courses import Courses
from application.models.coursesSchema import CoursesSchema
from application.models.platforms import Platforms
from application.models.ratings import Ratings
from application.models.keywords import Keywords
from application.models.keywordsSchema import KeywordsSchema
from application.models.tags import Tags
from application.models.coursesSearchSchema import CoursesSearchSchema
from application.models.ratingsSchema import RatingsSchema
from application.models.reviewsSchema import ReviewsSchema
from application.models.reviews import Reviews
from application.models.releases import Releases
from application.models.releasesSchema import ReleasesSchema
from application.models.releaseTypes import ReleaseTypes

from application.models.users import Users

mod = Blueprint(
    'courses',
    __name__,
    url_prefix='/api/v1/courses'
)

es = Elasticsearch(hosts=os.environ.get('ES_HOST'))

course_schema = CoursesSchema()
courses_schema = CoursesSchema(many=True)

course_search_schema = CoursesSearchSchema()

keyword_schema = KeywordsSchema()
keyword_schemas = KeywordsSchema(many=True)

rating_schema = RatingsSchema()
ratings_schema = RatingsSchema(many=True)

review_schema = ReviewsSchema()
reviews_schema = ReviewsSchema(many=True)

release_schema = ReleasesSchema()
releases_schema = ReleasesSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(courses_schema.dump(Courses.query.options().all()))


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
    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    # from flask import current_app
    #
    # message = json.dumps(json.dumps(course_search_schema.dump(course)))
    #
    # current_app.logger.info(current_app.topic.__dict__)
    #
    # with current_app.topic.get_producer() as producer:
    #     producer.produce(message.encode('ascii'))

    return course_schema.dump(course)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Courses.query.get(id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:id>', methods=['PUT'])
def update(id):
    course = Courses.query.filter_by(id=id).first()
    course.name = request.json.get('name', course.name)
    course.updated_on = func.now()

    db_session.commit()

    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    return jsonify(course_schema.dump(course))


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

    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    return keyword_schema.dump(keyword)


@mod.route('/<uuid:course_id>/keywords/<uuid:keyword_id>', methods=['GET'])
def keywords_get(course_id, keyword_id):
    return jsonify(keyword_schema.dump(Keywords.query.options().get(keyword_id)))


@mod.route('/<uuid:course_id>/keywords/', methods=['GET'])
def keywords_get_all(course_id):
    return jsonify(keyword_schemas.dump(Keywords.query.filter_by(course_id=course_id).options().all()))


@mod.route('/<uuid:course_id>/tag/', methods=['POST'])
def add_tag(course_id):
    if not request.json or not 'tag_id' in request.json:
        abort(400)

    tag_id = request.json['tag_id']
    course = Courses.query.get(course_id)
    tag = Tags.query.filter_by(id=tag_id).first()

    course.tags.append(tag)
    db_session.commit()

    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    return jsonify(course_schema.dump(course))


@mod.route('/<uuid:course_id>/ratings/', methods=['GET'])
def ratings_get_all(course_id):
    course = Courses.query.get(course_id)
    return jsonify(ratings_schema.dump(Ratings.query.filter_by(course=course).all()))


@mod.route('/<uuid:course_id>/ratings/<uuid:rating_id>', methods=['GET'])
def ratings_get(course_id, rating_id):
    course = Courses.query.get(course_id)
    return jsonify(rating_schema.dump(Ratings.query.filter_by(course=course, id=rating_id).first()))


@mod.route('/<uuid:course_id>/ratings/', methods=['POST'])
@jwt_required
def ratings_create(course_id):
    if not request.json or not 'points' in request.json:
        abort(400)

    points = request.json['points']

    course = Courses.query.get(course_id)

    current_user = get_jwt_identity()
    user = Users.query.filter_by(name=current_user).first()

    rating = Ratings(user=user, course=course, points=points)
    db_session.add(rating)
    db_session.commit()

    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    return rating_schema.dump(rating)


@mod.route('/<uuid:course_id>/ratings/<uuid:rating_id>', methods=['DELETE'])
@jwt_required
def ratings_delete(course_id, rating_id):
    db_session.delete(Ratings.query.get(rating_id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:course_id>/reviews/', methods=['GET'])
def reviews_get_all(course_id):
    course = Courses.query.get(course_id)
    return jsonify(reviews_schema.dump(Reviews.query.filter_by(course=course).all()))


@mod.route('/<uuid:course_id>/reviews/<uuid:review_id>', methods=['GET'])
def reviews_get(course_id, review_id):
    course = Courses.query.get(course_id)
    return jsonify(review_schema.dump(Reviews.query.filter_by(course=course, id=review_id).first()))


@mod.route('/<uuid:course_id>/reviews/', methods=['POST'])
@jwt_required
def reviews_create(course_id):
    if not request.json or not 'description' in request.json:
        abort(400)

    description = request.json['description']

    course = Courses.query.get(course_id)

    current_user = get_jwt_identity()

    user = Users.query.filter_by(name=current_user).first()

    review = Reviews(user=user, course=course, description=description)
    db_session.add(review)
    db_session.commit()

    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    return review_schema.dump(review)


@mod.route('/<uuid:course_id>/reviews/<uuid:review_id>', methods=['DELETE'])
@jwt_required
def reviews_delete(course_id, review_id):
    db_session.delete(Reviews.query.get(review_id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:course_id>/releases/', methods=['POST'])
def releases_create(course_id):
    course = Courses.query.get(course_id)

    name = request.json['name']
    description = request.json['description']
    release_type_id = request.json['release_type_id']

    release_type = ReleaseTypes.query.get(release_type_id)
    release = Releases(name, description, release_type)
    course.releases.append(release)

    course.updated_on = func.now()

    db_session.commit()

    es.index(index='courses', doc_type='title', id=course.id, body=json.dumps(course_search_schema.dump(course)))

    return release_schema.dump(release)
