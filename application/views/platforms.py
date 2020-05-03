from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func

from application.models.models import Platforms, PlatformsSchema, db_session

mod = Blueprint(
    'platforms',
    __name__,
    url_prefix='/api/v1/platforms'
)

platform_schema = PlatformsSchema()
platforms_schema = PlatformsSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(platforms_schema.dump(Platforms.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(platform_schema.dump(Platforms.query.get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = request.json['name']
    platform = Platforms(name)

    db_session.add(platform)
    db_session.commit()
    return platform_schema.dump(platform)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Platforms.query.get(id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:id>', methods=['PUT'])
def update(id):
    platform = Platforms.query.get(id)
    platform.name = request.json.get('name', platform.name)
    platform.updated_on = func.now()

    db_session.commit()
    return jsonify(platform_schema.dump(Platforms.query.get(id)))
