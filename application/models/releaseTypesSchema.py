from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema


class ReleaseTypesSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    name = fields.String()
    description = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    _links = Hyperlinks(
        {"self": URLFor("release_types.get", id="<id>"), "collection": URLFor("release_types.get_all")}
    )
