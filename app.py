import json
from datetime import datetime, timedelta

from handlers.orders.controller import ORDERS_BLUEPRINT
from handlers.users.controller import USERS_BLUEPRINT
from handlers.common.base_model import db
from handlers.users.models import User
from config import Config

from flask import Flask, make_response, request, jsonify
import jwt

app = Flask(__name__)

app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(ORDERS_BLUEPRINT, url_prefix="/v1/")
app.register_blueprint(USERS_BLUEPRINT, url_prefix="/v1/")


@app.route('/')
def index():
    print(json.dumps(app.config, default=str))
    return make_response('All is well!', 200)


@app.route('/login', methods=['POST'])
def login():
    auth = request.form

    if not auth or not auth.get('username') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query.filter_by(username=auth.get('username')).first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if user.pwd == auth.get('password'):
        token = jwt.encode({
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET'])

        return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


@app.after_request
def after_request(response):
    """
    Basically CORS middleware
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run()
