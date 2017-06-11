from flask import Flask, request
from flask_restful import Resource, reqparse
from flask_restful.utils import cors
from common import Message, search, utils


##
## Classes for request handlers
##

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


class FCEByID(Resource):
    @cors.crossdomain(origin='*')
    def get(self, courseid):
        result = search.get_fce_by_id(courseid, size=300)
        return format_response(result)


class FCEByInstructor(Resource):
    @cors.crossdomain(origin='*')
    @utils.word_limit
    def get(self, instructor):
        result = search.get_fce_by_instructor(instructor, size=300)
        return format_response(result)
