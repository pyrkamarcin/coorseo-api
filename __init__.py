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
from .views import auth
from .views import courses
from .views import platforms
from .views import publishers
from .views import profile
from .views import ratings
from .views import reviews

from .models.models import db_session, Users

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


@app.route('/logout')
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
