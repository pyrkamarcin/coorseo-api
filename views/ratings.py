from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func

from ..models import Ratings, RatingsSchema, db_session, Users

mod = Blueprint(
    'ratings',
    __name__,
    url_prefix='/api/ratings'
)

rating_schema = RatingsSchema()
ratings_schema = RatingsSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(ratings_schema.dump(Ratings.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(rating_schema.dump(Ratings.query.options().get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'points' in request.json:
        abort(400)

    if not request.json or not 'course' in request.json:
        abort(400)

    points = request.json['points']
    course_id = request.json['course']
    user_id = request.json['user']

    user = Users.query.get(user_id)

    rating = Ratings(user=user, points=points)
    rating.course_id = course_id

    db_session.add(rating)
    db_session.commit()
    return rating_schema.dump(rating)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Ratings.query.get(id))
    db_session.commit()
    return jsonify({'result': True})
