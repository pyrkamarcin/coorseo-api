from flask import Blueprint, request, jsonify, abort
from sqlalchemy import func

from application.models.models import Tags, TagsSchema, db_session

mod = Blueprint(
    'tags',
    __name__,
    url_prefix='/api/tags'
)

tag_schema = TagsSchema()
tags_schema = TagsSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(tags_schema.dump(Tags.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(tags_schema.dump(Tags.query.get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'name' in request.json:
        abort(400)
    name = request.json['name']
    description = request.json['description']
    tag = Tags(name, description)

    db_session.add(tag)
    db_session.commit()
    return tag_schema.dump(tag)


@mod.route('/<uuid:id>', methods=['DELETE'])
def delete(id):
    db_session.delete(Tags.query.get(id))
    db_session.commit()
    return jsonify({'result': True})


@mod.route('/<uuid:id>', methods=['PUT'])
def update(id):
    tag = Tags.query.get(id)
    tag.name = request.json.get('name', tag.name)
    tag.description = request.json.get('description', tag.description)
    tag.updated_on = func.now()

    db_session.commit()
    return jsonify(tag_schema.dump(Tags.query.get(id)))
