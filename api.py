from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from werkzeug.routing import BaseConverter

import config.settings as settings
import resources.course
from config.course import BASE_URL as COURSE_BASE_URL
import resources.fce
from config.fce import BASE_URL as FCE_BASE_URL
from common import Message, search, utils
# Raygun
if settings.RAYGUN_APIKEY is not None:
    from raygun4py.middleware import flask

app = Flask(__name__)
api = Api(app, catch_all_404s=True)

# Raygun
if settings.RAYGUN_APIKEY is not None:
    flask.Provider(app, settings.RAYGUN_APIKEY).attach()

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
api.add_resource(resources.course.CourseapiHome, COURSE_BASE_URL + '/')
# /course/:course-id
api.add_resource(resources.course.CourseDetail, COURSE_BASE_URL + r'/course/<regex("\d{2}-\d{3}"):courseid>/')
api.add_resource(resources.course.CourseDetailByTerm, COURSE_BASE_URL + r'/course/<regex("\d{2}-\d{3}"):courseid>/' + TERM_ENDPOINT)
# /instructor/:name
api.add_resource(resources.course.Instructor, COURSE_BASE_URL + '/instructor/<name>/')
api.add_resource(resources.course.InstructorByTerm, COURSE_BASE_URL + '/instructor/<name>/' + TERM_ENDPOINT)
# /building/:building
# api.add_resource(Building, COURSE_BASE_URL + '/building/<building>/')
api.add_resource(resources.course.BuildingByTerm, COURSE_BASE_URL + '/building/<building>/' + TERM_ENDPOINT)
# /room/:room
# api.add_resource(Room, COURSE_BASE_URL + '/room/<room>/')
api.add_resource(resources.course.RoomByTerm, COURSE_BASE_URL + '/room/<room>/' + TERM_ENDPOINT)
# building/:building/room/:room
api.add_resource(resources.course.BuildingRoom, COURSE_BASE_URL + '/building/<building>/room/<room>/')
api.add_resource(resources.course.BuildingRoomByTerm, COURSE_BASE_URL + '/building/<building>/room/<room>/' + TERM_ENDPOINT)
# datetime/:datetime
api.add_resource(resources.course.Datetime, COURSE_BASE_URL + '/datetime/<datetime_str>/')
api.add_resource(resources.course.DatetimeSpan, COURSE_BASE_URL + '/datetime/<datetime_str>/timespan/<span_str>/')

api.add_resource(resources.fce.FCEByID, FCE_BASE_URL + '/id/<courseid>/')
api.add_resource(resources.fce.FCEByInstructor, FCE_BASE_URL + '/instructor/<instructor>/')


if __name__ == '__main__':
    settings.DEBUG = True
    app.run(debug=True)
