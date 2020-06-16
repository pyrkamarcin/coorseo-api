import numpy as np

from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema


class ReleasesSchema(Schema):
    class Meta:
        ordered = True

    id = fields.UUID()

    name = fields.String()
    description = fields.String()
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    release_type = fields.Nested('ReleaseTypesSchema')
