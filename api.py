from flask import Flask
from flask_restful import Resource, Api
from werkzeug.routing import BaseConverter
import catalogsearcher_es

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
    def get(self, courseid=None, course_index=None):
        result = catalogsearcher_es.getCourseByID(courseid, course_index)
        course = result.get('course')
        return course

api.add_resource(HelloWorld, '/')
api.add_resource(CourseDetail, '/<regex("\d{2}-\d{3}"):courseid>/<regex("(f|s|m1|m2)\d{2}"):course_index>')


if __name__ == '__main__':
    app.run(debug=True)
