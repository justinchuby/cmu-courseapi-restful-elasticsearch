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


class CourseDetail(Resource):
    def get(self, courseid):
        result = search.getCourseByID(courseid, None)
        course = result.get('course')
        if course is not None:
            return {'course': course.dict()}
        return None


class CourseDetailByIndex(Resource):
    def get(self, courseid, course_index):
        result = search.getCourseByID(courseid, course_index)
        course = result.get('course')
        if course is not None:
            return {'course': course.dict()}
        elif result['response'].get('status') == '404':
            return {
                'status': '404',
                'error': {
                    'message': 'Cannot find %s in %s' % (courseid, course_index)
                }
            }, 404
        return {
            'status': '500',
            'error': {
                'message': 'Server Error'
            }
        }, 500


api.add_resource(HelloWorld, '/')
api.add_resource(CourseDetail, BASE_URL + '/course/<regex("\d{2}-\d{3}"):courseid>/')
api.add_resource(CourseDetailByIndex, BASE_URL + '/course/<regex("\d{2}-\d{3}"):courseid>/<regex("(f|s|m1|m2)\d{2}"):course_index>/')


if __name__ == '__main__':
    app.run(debug=True)
