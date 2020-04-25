from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func

from application.models.models import Publishers, PublishersSchema, db_session

mod = Blueprint(
    'publishers',
    __name__,
    url_prefix='/api/publishers'
)

publisher_schema = PublishersSchema()
publishers_schema = PublishersSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(publishers_schema.dump(Publishers.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(publisher_schema.dump(Publishers.query.get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = request.json['name']
    publisher = Publishers(name)

    db_session.add(publisher)
    db_session.commit()
    return publisher_schema.dump(publisher)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Publishers.query.get(id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:id>', methods=['PUT'])
def update(id):
    publisher = Publishers.query.get(id)
    publisher.name = request.json.get('name', publisher.name)
    publisher.updated_on = func.now()

    db_session.commit()
    return jsonify(publisher_schema.dump(Publishers.query.get(id)))
