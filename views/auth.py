from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, create_refresh_token, jwt_refresh_token_required,
    JWTManager, jwt_required, create_access_token,
    get_jwt_claims
)

auth = Blueprint('auth', __name__)


# https://flask-jwt-extended.readthedocs.io/en/stable/

@auth.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    # https://flask-jwt-extended.readthedocs.io/en/stable/add_custom_data_claims/
    ret = {
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200


@auth.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


@auth.route('/logout')
@jwt_required
def logout():
    return 'Logout'
