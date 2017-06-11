from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from werkzeug.routing import BaseConverter

import resources.course
import config
from config import BASE_URL
from common import Message, search, utils
# Raygun
if config.RAYGUN_APIKEY is not None:
    from raygun4py.middleware import flask

app = Flask(__name__)
api = Api(app, catch_all_404s=True)

# Raygun
if config.RAYGUN_APIKEY is not None:
    flask.Provider(app, config.RAYGUN_APIKEY).attach()

##
## Startup script
##
@app.before_first_request
def startup():
    # Initialize connection to ES server
    search.init_es_connection()


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

##
## Endpoint definitions
##

TERM_ENDPOINT = r'term/<regex("(f|s|m1|m2)\d{2}|current"):term>/'

api.add_resource(resources.course.HomeHome, '/')
api.add_resource(resources.course.CourseapiHome, BASE_URL + '/')
# /course/:course-id
api.add_resource(resources.course.CourseDetail, BASE_URL + r'/course/<regex("\d{2}-\d{3}"):courseid>/')
api.add_resource(resources.course.CourseDetailByTerm, BASE_URL + r'/course/<regex("\d{2}-\d{3}"):courseid>/' + TERM_ENDPOINT)
# /instructor/:name
api.add_resource(resources.course.Instructor, BASE_URL + '/instructor/<name>/')
api.add_resource(resources.course.InstructorByTerm, BASE_URL + '/instructor/<name>/' + TERM_ENDPOINT)
# /building/:building
# api.add_resource(Building, BASE_URL + '/building/<building>/')
api.add_resource(resources.course.BuildingByTerm, BASE_URL + '/building/<building>/' + TERM_ENDPOINT)
# /room/:room
# api.add_resource(Room, BASE_URL + '/room/<room>/')
api.add_resource(resources.course.RoomByTerm, BASE_URL + '/room/<room>/' + TERM_ENDPOINT)
# building/:building/room/:room
api.add_resource(resources.course.BuildingRoom, BASE_URL + '/building/<building>/room/<room>/')
api.add_resource(resources.course.BuildingRoomByTerm, BASE_URL + '/building/<building>/room/<room>/' + TERM_ENDPOINT)
# datetime/:datetime
api.add_resource(resources.course.Datetime, BASE_URL + '/datetime/<datetime_str>/')
api.add_resource(resources.course.DatetimeSpan, BASE_URL + '/datetime/<datetime_str>/timespan/<span_str>')


if __name__ == '__main__':
    config.DEBUG = True
    app.run(debug=True)
