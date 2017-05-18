from flask import Flask
from flask_restful import Resource, Api
from werkzeug.routing import BaseConverter
from config import *
import search

app = Flask(__name__)
api = Api(app)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter


class HelloWorld(Resource):
    def get(self, courseid=None, index=None):
        return {courseid: index}


##
## @brief      Gets the course detail.
##
## @param      courseid  The courseid
## @param      index     The Elasticsearch index
##
## @return     (dict, int) A course-api Course object or the error message, 
##             along with the http response code.
##
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


class CourseDetailByIndex(Resource):
    def get(self, courseid, term):
        return get_course_detail(courseid, term)


class Instructor(Resource):
    def get(self, name):
        result = search.get_course_by_instructor(name)
        response = result['course']
        return response


api.add_resource(HelloWorld, '/')
# /course/:course-id
api.add_resource(CourseDetail, BASE_URL + '/course/<regex("\d{2}-\d{3}"):courseid>/')
api.add_resource(CourseDetailByIndex, BASE_URL + '/course/<regex("\d{2}-\d{3}"):courseid>/term/<regex("(f|s|m1|m2)\d{2}"):term>/')
# /instructor/:name
api.add_resource(Instructor, BASE_URL + '/instructor/<name>/')



if __name__ == '__main__':
    app.run(debug=True)
