import logging

from handlers.orders.models import Order, Destination, Product
from handlers.users.models import User
from handlers.orders.schemas import DestinationSchema, OrderSchema
from utils.authorizers import authorized, authorized_admin

from flask import Blueprint, request, make_response, jsonify, g
from marshmallow import ValidationError

ORDERS_BLUEPRINT = Blueprint("orders", __name__)
logger = logging.getLogger(__name__)


def generate_destination_from_schema(payload: DestinationSchema):
    destination = Destination()
    destination.name = payload.get('name')
    destination.address = payload.get('address')
    destination.zipcode = payload.get('zipcode')
    destination.ext_num = payload.get('ext_num')
    destination.int_num = payload.get('int_num')
    destination.city = payload.get('city')
    destination.latitude = payload.get('latitude')
    destination.longitude = payload.get('longitude')
    destination.save()
    return destination


@ORDERS_BLUEPRINT.route('/orders/', methods=['GET'])
@authorized
def get_all_orders():
    if g.user.is_admin:
        orders = Order.query.all()
    else:
        orders = Order.query.filter_by(user_id=g.user.id).all()
    orders_response = [OrderSchema().dump(order) for order in orders]
    return make_response(jsonify(orders_response), 200)


@ORDERS_BLUEPRINT.route('/orders/<int:order_id>', methods=['GET'])
@authorized
def get_order(order_id):
    order = Order.query.get(order_id)

    if order:
        if not g.user.is_admin and order.user_id != g.user.id:
            return make_response(jsonify({"error": "you don't have access to this order"}), 401)

        order.user = User.query.get(order.user_id)
        order.destination = Destination.query.get(order.destination_id)
        order.origin = Destination.query.get(order.origin_id)
        return make_response(jsonify(OrderSchema().dump(order)), 200)
    return make_response(f"Order {order_id} doesn't exist", 404)


@ORDERS_BLUEPRINT.route('/orders/<int:order_id>', methods=['PATCH'])
@authorized
def patch_order(order_id):
    data_json = request.json
    try:
        user = g.user
        order = Order.query.get(order_id)
        if not order:
            return make_response(f"Order {order_id} doesn't exist", 404)
        if not g.user.is_admin and order.user_id != g.user.id:
            return make_response(jsonify({"error": "you don't have access to this order"}), 401)

        new_status = data_json["new_status"]
        if new_status not in Order.OrdersStatus.list():
            return make_response({"error": f"Status {new_status} is invalid"}, 404)
        if user.is_admin:
            order.status = Order.OrdersStatus[new_status].value
            return make_response(jsonify(OrderSchema().dump(order)), 200)
        else:
            # Check if the user is the order's owner, and he can only cancel
            if new_status == Order.OrdersStatus.cancelado.value:  # If the user is trying to cancel the order
                resolution = order.cancel()
                order.resolution = resolution
                return make_response(jsonify(OrderSchema().dump(order)), 200)
            # On any other status value we just go to the next status and ignore input
            order.move_forward()
            return make_response(jsonify(OrderSchema().dump(order)), 200)
    except Exception as e:
        return make_response({"error": f"{e.args[0]}"}, 503)


@ORDERS_BLUEPRINT.route('/orders/', methods=['POST'])
@authorized
def create_order():
    try:
        order_json = request.json
        # user
        user = g.user

        if isinstance(order_json['origin'], int):
            origin = Destination.query.get(order_json['origin'])
        else:
            origin_payload = DestinationSchema().load(order_json['origin'])
            origin = generate_destination_from_schema(origin_payload)

        if isinstance(order_json['destination'], int):
            destination = Destination.query.get(order_json['destination'])
        else:
            destination_payload = DestinationSchema().load(order_json['destination'])
            destination = generate_destination_from_schema(destination_payload)

        order = Order(user.id, origin.id, destination.id)
        for product in order_json['products']:
            if float(product["weight"]) > 25:
                raise Exception("Invalid weight, contact support")
            product_obj = Product(product["weight"], product["sku"])
            product_obj.save()
            order.add_product(product_obj)
        order.save()
        return make_response(jsonify(OrderSchema().dump(order)), 201)
    except ValidationError as err:
        return make_response(err.messages, 400)
    except Exception as e:
        return make_response({"error": f"{e.args[0]}"}, 503)


@ORDERS_BLUEPRINT.route('/destinations/', methods=['GET'])
@authorized_admin
def get_all_destinations():
    destinations = Destination.query.all()

    destinations_response = [DestinationSchema().dump(destination) for destination in destinations]
    return make_response(jsonify(destinations_response), 200)


@ORDERS_BLUEPRINT.route('/destinations/<int:destination_id>', methods=['GET'])
@authorized_admin
def get_destination(destination_id):
    destination = Destination.query.get(destination_id)
    if destination:
        return make_response(jsonify(DestinationSchema().dump(destination)), 200)
    return make_response(f"Destination {destination_id} doesn't exist", 404)


@ORDERS_BLUEPRINT.route('/destinations/', methods=['POST'])
@authorized
def create_destination():
    try:
        destination_payload = DestinationSchema().load(request.json)
        destination = generate_destination_from_schema(destination_payload)
        return make_response(jsonify(DestinationSchema().dump(destination)), 201)
    except ValidationError as err:
        return make_response(err.messages, 400)
    except Exception as e:
        return make_response({"error": f"{e.__cause__}"}, 503)
