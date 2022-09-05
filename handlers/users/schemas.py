from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(required=True, dump_only=True)
    date_created = fields.DateTime(required=False, dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=60), load_only=True)
