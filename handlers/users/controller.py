import json
import logging

from handlers.users.models import User
from handlers.users.schemas import UserSchema

from flask import Blueprint, request, make_response, jsonify
from marshmallow import ValidationError

USERS_BLUEPRINT = Blueprint("users", __name__)
logger = logging.getLogger(__name__)


@USERS_BLUEPRINT.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return make_response(jsonify({"error":"User doesn't exist"}), 404)

    return make_response(jsonify(UserSchema().dump(user)), 200)


@USERS_BLUEPRINT.route('/users/', methods=['POST'])
def create():
    try:
        user_payload = UserSchema().load(request.json)
        new_user = User(user_payload.get('username'), user_payload.get('password'))
        new_user.save()

        return make_response(jsonify(UserSchema().dump(new_user)), 201)
    except ValidationError as err:
        print(err.valid_data)
        return make_response(err.messages, 400)
    except Exception as e:
        return make_response({"error": f"{e.__cause__}"}, 503)
