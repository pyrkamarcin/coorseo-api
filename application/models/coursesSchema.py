import numpy as np

from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import fields, Schema

from application.models.users import Users


class CoursesSchema(Schema):
    class Meta:
        ordered = True

    @staticmethod
    def ratings_average_calculate(obj):
        point = []
        for rating in obj.ratings:
            point.append(rating.points)
        return np.average(point)

    id = fields.UUID()

    name = fields.String()
    # https://stackoverflow.com/questions/53606872/datetime-format-in-flask-marshmallow-schema
    created_on = fields.DateTime()
    updated_on = fields.DateTime()

    platform = fields.Nested('PlatformsSchema')
    publisher = fields.Nested('PublishersSchema')

    ratings = fields.Nested('RatingsSchema', many=True)
    ratings_count = fields.Function(lambda obj: len(obj.ratings))

    reviews = fields.Nested('ReviewsSchema', many=True)
    reviews_count = fields.Function(lambda obj: len(obj.reviews))

    tags = fields.Nested('TagsSchema', many=True)

    keywords = fields.Nested('KeywordsSchema', many=True)
    releases = fields.Nested('ReleasesSchema', many=True)

    _links = Hyperlinks(
        {"self": URLFor("courses.get", id="<id>"), "collection": URLFor("courses.get_all")}
    )
