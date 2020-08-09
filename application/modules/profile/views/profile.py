from flask import Blueprint, render_template

mod = Blueprint(
    'profile',
    __name__,
    url_prefix='/profile',
    template_folder='../templates',
    static_folder='static'
)


@mod.route('/')
def index():
    return render_template('index.html')


@mod.route('/list')
def list():
    return render_template('list.html')
