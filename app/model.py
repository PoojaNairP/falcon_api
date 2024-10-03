from marshmallow import Schema, fields,validate

class UserModel(Schema):

    name = fields.Str(required=True,
                      validate=validate.Length(1,100))

    email = fields.Str(required=True,
                       validate=validate.Email())

    age = fields.Int(required=True,
                     validate=validate.Range(1,120))





