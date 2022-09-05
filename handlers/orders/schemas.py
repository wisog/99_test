from decimal import Decimal

from handlers.users.schemas import UserSchema

from marshmallow import Schema, fields, validate, ValidationError


def validate_latitude(latitude):
    try:
        lat = Decimal(latitude)
        if lat < -90 or lat > 90:
            raise ValidationError("Latitude invalid")
    except:
        raise ValidationError("Latitude invalid")


def validate_longitude(longitude):
    try:
        lon = Decimal(longitude)
        if lon < -180 or lon > 180:
            raise ValidationError("Longitude invalid")
    except:
        raise ValidationError("Longitude invalid")


class ProductSchema(Schema):
    weight = fields.Decimal(required=True)
    size = fields.Str(required=False, dump_only=True)
    sku = fields.Str(required=True)


class DestinationSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    date_created = fields.DateTime(required=False, dump_only=True)
    latitude = fields.Str(validate=validate_latitude)
    longitude = fields.Str(validate=validate_longitude)
    name = fields.Str(required=False, validate=validate.Length(min=1, max=15))
    address = fields.Str(required=True, validate=validate.Length(min=1, max=250))
    zipcode = fields.Int(required=True)
    ext_num = fields.Str(required=True, validate=validate.Length(min=1, max=4))
    int_num = fields.Str(required=False, validate=validate.Length(min=1, max=4))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=60))


class OrderSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    date_created = fields.DateTime(required=False, dump_only=True)
    user = fields.Nested(UserSchema, only=("username",), dump_only=True)
    products = fields.List(fields.Nested(ProductSchema))
    origin = fields.Nested(DestinationSchema, dump_only=True)
    destination = fields.Nested(DestinationSchema, dump_only=True)
    status = fields.Str(dump_only=True)
    resolution = fields.Str(dump_only=True)
