from flask import Flask, request
from flask_restful import Resource, reqparse
from flask_restful.utils import cors
from common import Message, search, utils


##
## Classes for request handlers
##

class HomeHome(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        return {'message': Message.HOME_MESSAGE}


class CourseapiHome(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        return {'message': Message.API_ROOT_MESSAGE}


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
            'status': 404,
            'error': {
                'message': 'Cannot find %s in %s' % (courseid, index)
            }
        }
        code = 404
    elif (result['response'].get('status') == 404):
        response = {
            'status': 404,
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
    @cors.crossdomain(origin='*')
    def get(self, courseid):
        return get_course_detail(courseid, None)


class CourseDetailByTerm(Resource):
    @cors.crossdomain(origin='*')
    def get(self, courseid, term):
        return get_course_detail(courseid, term)


class Instructor(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, name):
        args = request.args
        fuzzy = False
        if 'fuzzy' in args:
            fuzzy = True
        result = search.get_courses_by_instructor(name, fuzzy=fuzzy, size=1000)
        return format_response(result)


class InstructorByTerm(Resource):
    fuzzy_parser = reqparse.RequestParser()
    fuzzy_parser.add_argument('fuzzy')

    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, name, term):
        args = request.args
        fuzzy = False
        if 'fuzzy' in args:
            fuzzy = True
        result = search.get_courses_by_instructor(name, fuzzy=fuzzy,
                                                  index=term, size=500)
        return format_response(result)


class BuildingByTerm(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, building, term):
        result = search.get_courses_by_building_room(building, None,
                                                     index=term, size=500)
        return format_response(result)


class RoomByTerm(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, room, term):
        result = search.get_courses_by_building_room(None, room,
                                                     index=term, size=500)
        return format_response(result)


class BuildingRoom(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, building, room):
        result = search.get_courses_by_building_room(building, room, size=500)
        return format_response(result)


class BuildingRoomByTerm(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, building, room, term):
        result = search.get_courses_by_building_room(building, room,
                                                     index=term, size=100)
        return format_response(result)


class Datetime(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, datetime_str):
        result = search.get_courses_by_datetime(datetime_str, size=500)
        return format_response(result)


class DatetimeSpan(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, datetime_str, span_str):
        result = search.get_courses_by_datetime(datetime_str, span_str, size=500)
        return format_response(result)
