import json

from elasticsearch import Elasticsearch
from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt_extended import jwt_required
from flask_uuid import FlaskUUID
from sqlalchemy import func
from sqlalchemy.orm.strategy_options import lazyload, joinedload
import uuid

from application.models.models import Courses, CoursesSchema, db_session, Platforms, Ratings

mod = Blueprint(
    'search',
    __name__,
    url_prefix='/api/search'
)

es = Elasticsearch(hosts='es01:9200')

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
                "fields": ["name", "*.name"],
                "fuzziness": "AUTO"
            }
        }
    }

    results = es.search(index="courses", doc_type="title", body=body)
    return jsonify(results)
