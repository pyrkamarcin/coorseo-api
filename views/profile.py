from flask import Blueprint, render_template
from ..models.models import Users, db_session

mod = Blueprint(
    'profile',
    __name__,
    url_prefix='/profile',
    template_folder='templates',
    static_folder='static'
)


@mod.route('/')
def index():
    return render_template('profile/index.html')


@mod.route('/list')
def list():
    users = Users.query.order_by(Users.email).all()
    return render_template('profile/list.html')
