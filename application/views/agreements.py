from flask import Blueprint, request, jsonify, abort

from application.models.models import Agreements, AgreementsSchema, db_session

mod = Blueprint(
    'agreements',
    __name__,
    url_prefix='/api/agreements'
)

agreement_schema = AgreementsSchema()
agreements_schema = AgreementsSchema(many=True)


@mod.route('/', methods=['GET'])
def get_all():
    return jsonify(agreements_schema.dump(Agreements.query.all()))


@mod.route('/<uuid:id>', methods=['GET'])
def get(id):
    return jsonify(agreement_schema.dump(Agreements.query.get(id)))


@mod.route('/', methods=['POST'])
def post():
    if not request.json or not 'title' in request.json:
        abort(400)
    title = request.json['title']
    agreement = Agreements(title)
    agreement.description = request.json['description']
    agreement.valid_from = request.json['valid_from']
    agreement.valid_to = request.json['valid_to']

    db_session.add(agreement)
    db_session.commit()
    return agreement_schema.dump(agreement)
