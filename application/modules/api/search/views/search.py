import json, os

from elasticsearch import Elasticsearch
from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt_extended import jwt_required
from flask_uuid import FlaskUUID
from sqlalchemy import func
from sqlalchemy.orm.strategy_options import lazyload, joinedload
import uuid

from application.models.courses import Courses
from application.models.coursesSchema import CoursesSchema
from application.models.platforms import Platforms
from application.models.ratings import Ratings

from application.shared.models import db_session

mod = Blueprint(
    'search',
    __name__,
    url_prefix='/api/v1/search'
)

es = Elasticsearch(hosts=os.environ.get('ES_HOST'), port=433, use_ssl=True)

course_schema = CoursesSchema()
courses_schema = CoursesSchema(many=True)


# https://stackoverflow.com/questions/54121646/elasticsearch-exceptions-requesterror-requesterror400-mapper-parsing-excepti

@mod.route('/', methods=['POST'])
def search():
    keyword = request.json['keyword']
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html#phrase-fuzziness
    body = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["name", "*.name", "*.description", "**.name", "tags"],
                "fuzziness": "AUTO"
            }
        }
    }

    results = es.search(index="courses", doc_type="title", body=body)
    return jsonify(results)
