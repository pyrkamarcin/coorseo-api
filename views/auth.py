import datetime
import threading
from functools import wraps

from flask import Blueprint, request, jsonify, url_for, render_template, flash
from flask_jwt_extended import (get_jwt_identity, create_refresh_token, jwt_refresh_token_required, create_access_token,
                                current_user)
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, TimedJSONWebSignatureSerializer
from passlib.hash import sha256_crypt

from ..models.models import db_session, Users, UsersSchema, UserEvents

import smtplib
from .. import app

auth = Blueprint('auth', __name__)

user_schema = UsersSchema()


# https://flask-jwt-extended.readthedocs.io/en/stable/

@auth.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing parameters."}), 400
    if not password:
        return jsonify({"msg": "Missing parameters."}), 400

    user = Users.query.filter_by(name=username).first()

    if user and not user.confirmed:
        return jsonify({"msg": "User is not confirmed."}), 406

    if sha256_crypt.verify(password, user.password):

        user_event = UserEvents(user, "correctly logged")
        db_session.add(user_event)
        db_session.commit()

        # https://flask-jwt-extended.readthedocs.io/en/stable/add_custom_data_claims/
        ret = {
            'id': user.id,
            'access_token': create_access_token(identity=username),
            'refresh_token': create_refresh_token(identity=username)
        }
        return jsonify(ret), 200
    else:
        return jsonify({"msg": "User is not authorized or not exist."}), 406


@auth.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


@auth.route('/register', methods=['POST'])
def register():
    # https://www.programcreek.com/python/example/101081/itsdangerous.URLSafeTimedSerializer
    def generate_confirmation_token(email):
        serializer = TimedJSONWebSignatureSerializer('SECRET_KEY')
        return serializer.dumps(email, salt='SECURITY_PASSWORD_SALT')

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Missing parameters."}), 400
    if not username:
        return jsonify({"msg": "Missing parameters."}), 400
    if not password:
        return jsonify({"msg": "Missing parameters."}), 400

    user = Users.query.filter_by(name=username).first()
    if user:
        return jsonify({"msg": "User exist."}), 406

    user = Users(email=email, name=username, password=password)

    db_session.add(user)
    db_session.commit()

    user_event = UserEvents(user, "registered user")
    db_session.add(user_event)
    db_session.commit()

    token = generate_confirmation_token(user.email)

    def send_async_email(app, to, confirm_url):
        with app.app_context():
            sender = 'no-reply@example.com'
            message = "Confirmation: {}".format(confirm_url)
            server = smtplib.SMTP('localhost:1025')
            server.login(sender, password)
            server.sendmail(sender, to, message)
            server.quit()

    def send_email(to, confirm_url):
        thr = threading.Thread(target=send_async_email, args=[app, to, confirm_url])
        thr.start()
        return thr

    confirm_url = url_for('auth.confirmation', token=token, _external=True)
    send_email(user.email, confirm_url)

    user_event = UserEvents(user, "confirmation email sender")
    db_session.add(user_event)

    db_session.commit()
    return user_schema.dump(user)


@auth.route('/confirmation/<token>', methods=['GET'])
def confirmation(token):
    def confirm_token(token):
        serializer = TimedJSONWebSignatureSerializer('SECRET_KEY', expires_in=3600)
        try:
            email = serializer.loads(
                token,
                salt='SECURITY_PASSWORD_SALT'
            )
        except:
            return False
        return email

    try:
        email = confirm_token(token)
    except:
        return jsonify({"msg": "Damn it!"}), 406
    user = Users.query.filter_by(email=email).first()
    if user.confirmed:
        return jsonify({"msg": "Damn it!"}), 406
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db_session.add(user)
        db_session.commit()
    return jsonify({"msg": "Confirmed!"}), 200
