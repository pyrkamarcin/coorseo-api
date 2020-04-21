from __future__ import absolute_import, print_function

from flask import (Flask)
from flask_jwt import JWT
from flask_jwt_extended import JWTManager

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_uuid import FlaskUUID
from werkzeug.security import safe_str_cmp
from passlib.hash import pbkdf2_sha256

# from .views import home
from .views import auth
from .views import courses
from .views import platforms
from .views import publishers
from .views import profile
from .views import ratings
from .views import reviews

from .models import db_session, Users

# def authenticate(username, password):
#     user = Users.query.filter_by(name=username).first()
#
#     if user and password == user.password:
#         return user
#
#
# def identity(payload):
#     user_id = payload['identity']
#     return Users.query.get(user_id)


app = Flask(__name__, static_url_path='/static')
app.config['TESTING'] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

jwt = JWTManager(app)

flask_uuid = FlaskUUID()
flask_uuid.init_app(app)

# app.register_blueprint(home.mod)
app.register_blueprint(auth.auth)
app.register_blueprint(courses.mod)
app.register_blueprint(platforms.mod)
app.register_blueprint(publishers.mod)
app.register_blueprint(profile.mod)
app.register_blueprint(ratings.mod)
app.register_blueprint(reviews.mod)


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
