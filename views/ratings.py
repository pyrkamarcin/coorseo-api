from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from sqlalchemy import func

from ..models.models import Ratings, RatingsSchema, db_session, Users

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
@jwt_required
def post():
    if not request.json or not 'points' in request.json:
        abort(400)

    if not request.json or not 'course' in request.json:
        abort(400)

    points = request.json['points']
    course_id = request.json['course']

    current_user = get_jwt_identity()

    user = Users.query.filter_by(name=current_user).first()

    rating = Ratings(user=user, points=points)
    rating.course_id = course_id

    db_session.add(rating)
    db_session.commit()
    return rating_schema.dump(rating)


@mod.route('/<uuid:id>', methods=['DELETE'])
@jwt_required
def delete(id):
    db_session.delete(Ratings.query.get(id))
    db_session.commit()
    return jsonify({'result': True})
