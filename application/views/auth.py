from flask import Blueprint, render_template, session, redirect, url_for, request, flash, g, jsonify, abort, json
import smtplib
import datetime
import threading

from flask import (Flask)
from flask_jwt_extended import JWTManager, jwt_required, get_raw_jwt
from flask_mail import Mail
from flask_uuid import FlaskUUID

from flask import request, jsonify, url_for
from flask_jwt_extended import (get_jwt_identity, create_refresh_token, jwt_refresh_token_required, create_access_token)
from itsdangerous import TimedJSONWebSignatureSerializer
from passlib.hash import sha256_crypt

from flask import current_app
from sqlalchemy import JSON

from application.models.models import db_session, Users, UsersSchema, UserEvents, UserAgreements, Agreements, \
    UserAgreementsSchema

auth = Blueprint(
    'auth',
    __name__,
    url_prefix='/api/v1/user'
)


def email_from_confirm_token(token):
    serializer = TimedJSONWebSignatureSerializer('SECRET_KEY', expires_in=3600)
    try:
        email = serializer.loads(
            token,
            salt='SECURITY_PASSWORD_SALT'
        )
    except:
        return False
    return email


def send_async_email(to, confirm_url):
    sender = 'no-reply@example.com'
    message = "Verify: {}".format(confirm_url)
    server = smtplib.SMTP('mailhog:1025')
    server.login(sender, "sample")
    server.sendmail(sender, to, message)
    server.quit()


def send_email(to, confirm_url):
    thr = threading.Thread(target=send_async_email, args=[to, confirm_url])
    thr.start()
    return thr


# https://www.programcreek.com/python/example/101081/itsdangerous.URLSafeTimedSerializer
def generate_confirmation_token(email):
    serializer = TimedJSONWebSignatureSerializer('SECRET_KEY')
    return serializer.dumps(email, salt='SECURITY_PASSWORD_SALT')


user_schema = UsersSchema()
user_agreements_schema = UserAgreementsSchema()


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
        user_event = UserEvents(user, "not confirmed logging", dict(request.headers))
        db_session.add(user_event)
        db_session.commit()
        return jsonify({"msg": "User is not confirmed."}), 406

    if sha256_crypt.verify(password, user.password):

        user_event = UserEvents(user, "correctly logged", dict(request.headers))
        db_session.add(user_event)

        # https://flask-jwt-extended.readthedocs.io/en/stable/add_custom_data_claims/
        ret = {
            'id': user.id,
            'access_token': create_access_token(identity=username),
            'refresh_token': create_refresh_token(identity=username)
        }

        user_event = UserEvents(user, "generated tokens",
                                {"access_token": ret.get("access_token"), "refresh_token": ret.get("refresh_token")})
        db_session.add(user_event)
        db_session.commit()
        return jsonify(ret), 200
    else:
        user_event = UserEvents(user, "not authorized logging", dict(request.headers))
        db_session.add(user_event)
        db_session.commit()
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

    confirm_url = url_for('auth.confirmation', token=token, _external=True)
    send_email(user.email, confirm_url)

    user_event = UserEvents(user, "confirmation email sender")
    db_session.add(user_event)

    db_session.commit()
    return user_schema.dump(user)


@auth.route('/resend_confirmation', methods=['POST'])
def resend_confirmation():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)
    username = request.json.get('username', None)
    if not email:
        return jsonify({"msg": "Missing parameters."}), 400
    if not username:
        return jsonify({"msg": "Missing parameters."}), 400

    user = Users.query.filter_by(name=username, email=email).first()

    if user and user.confirmed:
        return jsonify({"msg": "User is confirmed."}), 406

    token = generate_confirmation_token(user.email)

    confirm_url = url_for('auth.confirmation', token=token, _external=True)
    send_email(user.email, confirm_url)

    user_event = UserEvents(user, "confirmation email sender again")
    db_session.add(user_event)

    db_session.commit()
    return user_schema.dump(user)


@auth.route('/confirmation/<token>', methods=['GET'])
def confirmation(token):
    try:
        email = email_from_confirm_token(token)
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


@auth.route('/password', methods=['POST'])
def password_request():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not exist."}), 406

    token = generate_confirmation_token(user.email)

    confirm_url = url_for('auth.password_change', token=token, _external=True)
    send_email(user.email, confirm_url)

    user_event = UserEvents(user, "password_change email sender")
    db_session.add(user_event)

    return jsonify({"msg": "Email send."}), 200


@auth.route('/password/<token>', methods=['POST'])
def password_change(token):
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    new_password = request.json.get('password', None)

    try:
        email = email_from_confirm_token(token)
    except:
        return jsonify({"msg": "Token is not valid."}), 406

    user = Users.query.filter_by(email=email).first()

    if user and not user.confirmed:
        return jsonify({"msg": "User is not confirmed."}), 406

    user.password = sha256_crypt.encrypt(new_password)
    db_session.add(user)
    db_session.commit()
    return jsonify({"msg": "Password changed."}), 200


@auth.route('/agreements', methods=['POST'])
@jwt_required
def add_agreements():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    agreement_id = request.json.get('agreement_id', None)
    if not agreement_id:
        return jsonify({"msg": "Missing parameters."}), 400

    is_accepted = request.json.get('is_accepted', None)

    current_user = get_jwt_identity()

    user = Users.query.filter_by(name=current_user).first()
    agreement = Agreements.query.filter_by(id=agreement_id).first()

    existing_user_agreements = UserAgreements.query.filter_by(user=user, agreement=agreement).first()

    if existing_user_agreements:
        return jsonify({"msg": "User_Agreement exist."}), 400

    user_agreements = UserAgreements(user=user, agreement=agreement, is_accepted=is_accepted)

    user_agreements.is_read = True

    db_session.add(user_agreements)
    db_session.commit()
    return jsonify(user_agreements_schema.dump(user_agreements))


@auth.route('/agreements', methods=['GET'])
@jwt_required
def get_agreements():
    current_user = get_jwt_identity()

    user = Users.query.filter_by(name=current_user).first()
    user_agreements = UserAgreements.query.filter_by(user=user).order_by("created_on").all()

    return jsonify(user_agreements_schema.dump(user_agreements, many=True))
