from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func

from ..models import Reviews, ReviewsSchema, db_session, Users

mod = Blueprint(
    'reviews',
    __name__,
    url_prefix='/api/reviews'
)

review_schema = ReviewsSchema()
reviews_schema = ReviewsSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(reviews_schema.dump(Reviews.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(review_schema.dump(Reviews.query.options().get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'description' in request.json:
        abort(400)

    if not request.json or not 'course' in request.json:
        abort(400)

    description = request.json['description']
    course_id = request.json['course']
    user_id = request.json['user']

    user = Users.query.get(user_id)

    review = Reviews(user=user, description=description)
    review.course_id = course_id

    db_session.add(review)
    db_session.commit()
    return review_schema.dump(review)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Reviews.query.get(id))
    db_session.commit()
    return jsonify({'result': True})
