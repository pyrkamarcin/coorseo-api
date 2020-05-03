from __future__ import absolute_import, print_function

import smtplib
import datetime
import threading

from elasticsearch import Elasticsearch
from flask import (Flask)
from flask_jwt_extended import JWTManager, jwt_required, get_raw_jwt
from flask_mail import Mail
from flask_uuid import FlaskUUID

from flask import request, jsonify, url_for
from flask_jwt_extended import (get_jwt_identity, create_refresh_token, jwt_refresh_token_required, create_access_token)
from itsdangerous import TimedJSONWebSignatureSerializer
from passlib.hash import sha256_crypt

from application.models.models import db_session, Users, UsersSchema, UserEvents

from application.views import auth
from application.views import home
from application.views import courses
from application.views import platforms
from application.views import publishers
from application.views import profile
from application.views import search
from application.views import tags
from application.views import agreements

app = Flask(__name__, static_url_path='/static')

app.config.from_object('application.config.Config')

mail = Mail(app)

jwt = JWTManager(app)
blacklist = set()

flask_uuid = FlaskUUID()
flask_uuid.init_app(app)

app.register_blueprint(auth.auth)
app.register_blueprint(home.mod)
app.register_blueprint(courses.mod)
app.register_blueprint(platforms.mod)
app.register_blueprint(publishers.mod)
app.register_blueprint(profile.mod)
app.register_blueprint(search.mod)
app.register_blueprint(tags.mod)
app.register_blueprint(agreements.mod)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


@app.route('/api/v1/user/logout', methods=['GET'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200
