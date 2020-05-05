import numpy as np

from marshmallow import fields, Schema

from application.models.users import Users


class CoursesSearchSchema(Schema):
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

    platform = fields.Nested('PlatformsSchema', only=["name"])
    publisher = fields.Nested('PublishersSchema', only=["name"])

    ratings = fields.Nested('RatingsSchema', many=True)
    ratings_count = fields.Function(lambda obj: len(obj.ratings))

    reviews = fields.Nested('ReviewsSchema', many=True)
    reviews_count = fields.Function(lambda obj: len(obj.reviews))

    tags = fields.Nested('TagsSchema', many=True, only=['name'])
    keywords = fields.Nested('KeywordsSchema', many=True)
