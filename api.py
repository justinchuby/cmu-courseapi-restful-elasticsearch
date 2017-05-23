from flask import Flask
from flask_restful import Resource, Api
from werkzeug.routing import BaseConverter
from config import *
import search


app = Flask(__name__)
api = Api(app)


@app.before_first_request
def startup():
    search.init_es_connection()


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter


class HomeHome(Resource):
    def get(self):
        return {'message': 'Hoooray! You are connected.'}


class CourseapiHome(Resource):
    def get(self):
        return {'message': 'Course API by ScottyLabs!'}


def format_response(search_result):
    # requires search_result to be a dictionary
    res = search_result.pop('response')
    code = 200

    if res.get('status') is None:
        response = search_result
    elif res.get('status') == 404:
        response = {
            'status': 404,
            'error': {
                'message': 'Not Found Error'
            }
        }
        code = 404
    elif res.get('status') == 400:
        response = {
            'status': 400,
            'error': res.get('error')
        }
        code = 400
    else:
        response = {
            'status': 500,
            'error': {
                'message': 'Server Error'
            }
        }
        code = 500
    return response, code


#
#
# @brief      Gets the course detail.
#
# @param      courseid  The courseid
# @param      index     The Elasticsearch index
#
# @return     (dict, int) A course-api Course object or the error message,
#             along with the http response code.
#
def get_course_detail(courseid, index):
    result = search.get_course_by_id(courseid, index)
    course = result.get('course')

    if course is not None:
        response = {'course': course}
        code = 200
    elif 'error' not in result['response']:
        # The course does not exist in the given index
        response = {
            'status': '404',
            'error': {
                'message': 'Cannot find %s in %s' % (courseid, index)
            }
        }
        code = 404
    elif (result['response'].get('status') == 404):
        response = {
            'status': '404',
            'error': {
                'message': 'Cannot find %s in %s' % (courseid, index)
            }
        }
        code = 404
    else:
        response = {
            'status': 500,
            'error': {
                'message': 'Server Error'
            }
        }
        code = 500
    return response, code


class CourseDetail(Resource):
    def get(self, courseid):
        return get_course_detail(courseid, None)


class CourseDetailByTerm(Resource):
    def get(self, courseid, term):
        return get_course_detail(courseid, term)


class Instructor(Resource):
    def get(self, name):
        result = search.get_courses_by_instructor(name)
        return format_response(result)


class InstructorByTerm(Resource):
    def get(self, name, term):
        result = search.get_courses_by_instructor(name, index=term)
        return format_response(result)


# class Building(Resource):
#     def get(self, building):
#         result = search.get_courses_by_building_room(building, None)
#         return format_response(result)


class BuildingByTerm(Resource):
    def get(self, building, term):
        result = search.get_courses_by_building_room(building, None, index=term)
        return format_response(result)


class Room(Resource):
    def get(self, room):
        result = search.get_courses_by_building_room(None, room)
        return format_response(result)


class RoomByTerm(Resource):
    def get(self, room, term):
        result = search.get_courses_by_building_room(None, room, index=term)
        return format_response(result)


class BuildingRoom(Resource):
    def get(self, building, room):
        result = search.get_courses_by_building_room(building, room)
        return format_response(result)


class BuildingRoomByTerm(Resource):
    def get(self, building, room, term):
        result = search.get_courses_by_building_room(building, room, index=term)
        return format_response(result)


class Datetime(Resource):
    def get(self, date_time_str):
        result = search.get_courses_by_datetime(date_time_str)
        return format_response(result)


TERM_ENDPOINT = r'term/<regex("(f|s|m1|m2)\d{2}|current"):term>/'

api.add_resource(HomeHome, '/')
api.add_resource(CourseapiHome, BASE_URL + '/')
# /course/:course-id
api.add_resource(CourseDetail, BASE_URL + r'/course/<regex("\d{2}-\d{3}"):courseid>/')
api.add_resource(CourseDetailByTerm, BASE_URL + r'/course/<regex("\d{2}-\d{3}"):courseid>/' + TERM_ENDPOINT)
# /instructor/:name
api.add_resource(Instructor, BASE_URL + '/instructor/<name>/')
api.add_resource(InstructorByTerm, BASE_URL + '/instructor/<name>/' + TERM_ENDPOINT)
# /building/:building
# api.add_resource(Building, BASE_URL + '/building/<building>/')
api.add_resource(BuildingByTerm, BASE_URL + '/building/<building>/' + TERM_ENDPOINT)
# /room/:room
# api.add_resource(Room, BASE_URL + '/room/<room>/')
api.add_resource(RoomByTerm, BASE_URL + '/room/<room>/' + TERM_ENDPOINT)
# building/:building/room/:room
api.add_resource(BuildingRoom, BASE_URL + '/building/<building>/room/<room>/')
api.add_resource(BuildingRoomByTerm, BASE_URL + '/building/<building>/room/<room>/' + TERM_ENDPOINT)
# datetime/:datetime
api.add_resource(Datetime, BASE_URL + '/datetime/<date_time_str>/')


if __name__ == '__main__':
    app.run(debug=True)

