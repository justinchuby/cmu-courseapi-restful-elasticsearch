from flask import Flask, request
from flask_restful import Resource
from common import Message, search, utils


##
## Classes for request handlers
##

class HomeHome(Resource):
    def get(self):
        return {'message': Message.HOME_MESSAGE}


class CourseapiHome(Resource):
    def get(self):
        return {'message': Message.API_ROOT_MESSAGE}


def is_valid_field(field):
    # Currently only desc is allowed to be filtered out
    return field == 'desc'


def parse_url_array(args, field):
    if field in args:
        return args[field].split(',')
    return None


def format_response(search_result, filtered_fields=None):
    if filtered_fields:
        for field in filtered_fields:
            if is_valid_field(field):
                # Assumed that courses field is always in the response
                for course in search_result['courses']:
                    course[field] = None

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
    def get(self, courseid):
        return get_course_detail(courseid, None)


class CourseDetailByTerm(Resource):
    def get(self, courseid, term):
        return get_course_detail(courseid, term)


class CourseDetailAllTerms(Resource):
    def get(self, courseid):
        result = search.get_courses_by_id(courseid)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class Instructor(Resource):
    @utils.word_limit
    def get(self, name):
        args = request.args
        fuzzy = False
        if 'fuzzy' in args:
            fuzzy = True
        result = search.get_courses_by_instructor(name, fuzzy=fuzzy, size=1000)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class InstructorByTerm(Resource):
    @utils.word_limit
    def get(self, name, term):
        args = request.args
        fuzzy = False
        if 'fuzzy' in args:
            fuzzy = True
        result = search.get_courses_by_instructor(name, fuzzy=fuzzy,
                                                  index=term, size=500)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class BuildingByTerm(Resource):
    @utils.word_limit
    def get(self, building, term):
        result = search.get_courses_by_building_room(building, None,
                                                     index=term, size=500)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class RoomByTerm(Resource):
    @utils.word_limit
    def get(self, room, term):
        result = search.get_courses_by_building_room(None, room,
                                                     index=term, size=500)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class BuildingRoom(Resource):
    @utils.word_limit
    def get(self, building, room):
        result = search.get_courses_by_building_room(building, room, size=500)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class BuildingRoomByTerm(Resource):
    @utils.word_limit
    def get(self, building, room, term):
        result = search.get_courses_by_building_room(building, room,
                                                     index=term, size=100)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class Datetime(Resource):
    @utils.word_limit
    def get(self, datetime_str):
        result = search.get_courses_by_datetime(datetime_str, size=500)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class DatetimeSpan(Resource):
    @utils.word_limit
    def get(self, datetime_str, span_str):
        result = search.get_courses_by_datetime(datetime_str, span_str, size=500)
        filtered_fields = parse_url_array(request.args, 'filtered_fields')
        return format_response(result, filtered_fields)


class Search(Resource):
    def get(self):
        args = request.args
        result = search.get_courses_by_searching(args, size=500)
        filtered_fields = parse_url_array(args, 'filtered_fields')
        return format_response(result, filtered_fields)
