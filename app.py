import json

from handlers.orders.controller import ORDERS_BLUEPRINT
from handlers.users.controller import USERS_BLUEPRINT
from handlers.common.base_model import db
from config import Config

from flask import Flask, make_response

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
