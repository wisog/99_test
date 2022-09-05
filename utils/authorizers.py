import functools

from handlers.users.models import User

from flask import request, make_response, g


def get_token_from_raw_authorization(raw_token):
    if raw_token is None or raw_token == "":
        return None
    raw_token_sections = raw_token.split(' ')
    if len(raw_token_sections) < 2:
        return None
    return raw_token_sections[1]


def authorized(func):
    """Verifies user is authorized to perform any subsequent actions.

    Args:
        func (function): Function to be wrapped and invoked.

    Returns:
        function: Wrapped/decorated function to be invoked.
    """
    @functools.wraps(func)
    def wrapper_authorized(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return make_response({"error": "Don't have authorization"}, 401)

        token = get_token_from_raw_authorization(token)
        if not token:
            return make_response({"error": "Don't have authorization"}, 401)

        user_id = User.decode_token(token)
        if not isinstance(user_id, int):
            return make_response({"error": "Invalid request"}, 400)

        user = User.query.get(user_id)
        if not user:
            return make_response({"error": "User doesn't exist"}, 400)

        g.user = user  # g's lifecycle is request based

        return func(*args, **kwargs)
    return wrapper_authorized


def authorized_admin(func):
    """Verifies user is authorized to perform any subsequent actions.

    Args:
        func (function): Function to be wrapped and invoked.

    Returns:
        function: Wrapped/decorated function to be invoked.
    """
    @functools.wraps(func)
    def wrapper_authorized(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return make_response({"error": "Don't have authorization"}, 401)

        token = get_token_from_raw_authorization(token)
        if not token:
            return make_response({"error": "Don't have authorization"}, 401)

        user_id = User.decode_token(token)
        if not isinstance(user_id, int):
            return make_response({"error": "Invalid request"}, 400)

        user = User.query.get(user_id)
        if not user:
            return make_response({"error": "User doesn't exist"}, 400)
        if not user.is_admin:
            return make_response({"error": "User doesn't have access"}, 401)
        g.user = user  # g's lifecycle is request based

        return func(*args, **kwargs)
    return wrapper_authorized
