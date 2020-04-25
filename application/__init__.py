from __future__ import absolute_import, print_function

from flask import (Flask, jsonify, url_for, render_template)
from flask_jwt_extended import JWTManager, jwt_required, get_raw_jwt
from flask_mail import Mail, Message
from flask_uuid import FlaskUUID

app = Flask(__name__, static_url_path='/static')
app.config['TESTING'] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_TOKEN_LOCATION'] = 'headers'
app.config['JWT_ALGORITHM'] = 'HS512'
app.config['SECRET_KEY'] = 'HxGIR23yK41si8zd9t9kKTEzQu5IyWetsGzrKtPCe294P4ACyselq4McFarahci'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.config.update(
    MAIL_SERVER='localhost',
    MAIL_PORT=1025,
    MAIL_USERNAME='test',
    MAIL_PASSWORD='test'
)

mail = Mail(app)

jwt = JWTManager(app)
blacklist = set()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


flask_uuid = FlaskUUID()
flask_uuid.init_app(app)

# from .views import home
# from views import auth
from application.views import courses
from application.views import platforms
from application.views import publishers
from application.views import profile
from application.views import ratings
from application.views import reviews

from application.models.models import db_session, Users

# app.register_blueprint(home.mod)
# app.register_blueprint(auth.auth)
app.register_blueprint(courses.mod)
app.register_blueprint(platforms.mod)
app.register_blueprint(publishers.mod)
app.register_blueprint(profile.mod)
app.register_blueprint(ratings.mod)
app.register_blueprint(reviews.mod)


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


import datetime
import threading
from functools import wraps

from flask import Blueprint, request, jsonify, url_for, render_template, flash
from flask_jwt_extended import (get_jwt_identity, create_refresh_token, jwt_refresh_token_required, create_access_token,
                                current_user)
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, TimedJSONWebSignatureSerializer
from passlib.hash import sha256_crypt

from application.models.models import db_session, Users, UsersSchema, UserEvents

import smtplib

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
            server = smtplib.SMTP('mailhog:1025')
            server.login(sender, "sample")
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


@auth.route('/resend_confirmation', methods=['POST'])
def resend_confirmation():
    # https://www.programcreek.com/python/example/101081/itsdangerous.URLSafeTimedSerializer
    def generate_confirmation_token(email):
        serializer = TimedJSONWebSignatureSerializer('SECRET_KEY')
        return serializer.dumps(email, salt='SECURITY_PASSWORD_SALT')

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

    def send_async_email(app, to, confirm_url):
        with app.app_context():
            sender = 'no-reply@example.com'
            message = "Confirmation: {}".format(confirm_url)
            server = smtplib.SMTP('mailhog:1025')
            server.login(sender, "sample")
            server.sendmail(sender, to, message)
            server.quit()

    def send_email(to, confirm_url):
        thr = threading.Thread(target=send_async_email, args=[app, to, confirm_url])
        thr.start()
        return thr

    confirm_url = url_for('auth.confirmation', token=token, _external=True)
    send_email(user.email, confirm_url)

    user_event = UserEvents(user, "confirmation email sender again")
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


@auth.route('/password', methods=['POST'])
def password_request():
    def generate_confirmation_token(email):
        serializer = TimedJSONWebSignatureSerializer('SECRET_KEY')
        return serializer.dumps(email, salt='SECURITY_PASSWORD_SALT')

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get('email', None)

    user = Users.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "User not exist."}), 406

    token = generate_confirmation_token(user.email)

    def send_async_email(app, to, confirm_url):
        with app.app_context():
            sender = 'no-reply@example.com'
            message = "Verify: {}".format(confirm_url)
            server = smtplib.SMTP('mailhog:1025')
            server.login(sender, "sample")
            server.sendmail(sender, to, message)
            server.quit()

    def send_email(to, confirm_url):
        thr = threading.Thread(target=send_async_email, args=[app, to, confirm_url])
        thr.start()
        return thr

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
        return jsonify({"msg": "Token is not valid."}), 406

    user = Users.query.filter_by(email=email).first()

    if user and not user.confirmed:
        return jsonify({"msg": "User is not confirmed."}), 406

    user.password = sha256_crypt.encrypt(new_password)
    db_session.add(user)
    db_session.commit()
    return jsonify({"msg": "Password changed."}), 200


@app.route('/logout')
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

#
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')
