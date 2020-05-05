from flask import Blueprint, request, jsonify, abort

from application.models.models import db_session, ReleaseTypesSchema, ReleaseTypes

mod = Blueprint(
    'release_types',
    __name__,
    url_prefix='/api/v1/release_types'
)

release_type_schema = ReleaseTypesSchema()
release_types_schema = ReleaseTypesSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(release_types_schema.dump(ReleaseTypes.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(release_type_schema.dump(ReleaseTypes.query.options().get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'name' in request.json:
        abort(400)
    if not request.json or not 'description' in request.json:
        abort(400)

    name = request.json['name']
    description = request.json['description']

    release_type = ReleaseTypes(name=name, description=description)

    db_session.add(release_type)
    db_session.commit()
    return release_type_schema.dump(release_type)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(ReleaseTypes.query.get(id))
    db_session.commit()
    return jsonify({'result': True})
