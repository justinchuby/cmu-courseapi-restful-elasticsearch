import re
import copy
import json
import arrow
import elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from elasticsearch_dsl.connections import connections
from config import ES_HOSTS, ES_HTTP_AUTH
import utils


##
## @brief      The Searcher object that parses input and generates queries.
##
class Searcher(object):
    _doc_type = None
    _default_size = 5

    ##
    ## @brief      init
    ##
    ## @param      self
    ## @param      s           The query text
    ##
    def __init__(self, raw_query, index=None, size=_default_size):
        self.raw_query = copy.deepcopy(raw_query)
        self.index = index
        self.size = size
        self.doc_type = self._doc_type

    def __repr__(self):
        return "<Searcher Object: rawQuery={}>".format(repr(self.raw_query))

    def execute(self):
        # if index is None:
        #     index = ALL_COURSES_INDEX
        response = self.fetch(self.generate_query(), self.index,
                              self.size, doc_type=self.doc_type)
        return response

    @staticmethod
    def fetch(query, index, size=5, doc_type=None):
        s = Search(index=index, doc_type=doc_type).query(query)
        s.size = size
        try:
            response = s.execute()
        except elasticsearch.exceptions.NotFoundError as e:
            # print(formatErrMsg(e, "ES"))
            response = e.info
        except elasticsearch.exceptions.RequestError as e:
            # print(formatErrMsg(e, "ES"))
            response = e.info
        except elasticsearch.exceptions.TransportError as e:
            # print(formatErrMsg(e, "ES"))
            response = e.info

        return response

    ##
    ## @brief      Generate the query for the database.
    ##
    ## @return     (dict) The query for querying the database.
    ##
    def generate_query(self):
        return self.construct_query_from_raw(self.raw_query)

    @staticmethod
    def construct_query_from_raw(raw_query):
        query = Q()
        return query


class CourseSearcher(Searcher):
    _doc_type = 'course'
    _default_size = 5

    def __init__(self, raw_query, index=None, size=_default_size):
        super().__init__(raw_query, index, size)

    @staticmethod
    def construct_query_from_raw(raw_query):
        query = Q()
        if 'courseid' in raw_query:
            query &= Q('term', id=raw_query['courseid'][0])

        if 'instructor' in raw_query:
            instructor = " ".join(raw_query['instructor'])
            lec_name_query = Q('match', lectures__instructors=instructor)
            sec_name_query = Q('match', sections__instructors=instructor)

            query &= Q('bool', should=[Q('nested', query=lec_name_query, path='lectures', inner_hits={}),
                                       Q('nested', query=sec_name_query, path='sections', inner_hits={})])

        # TODO: check if DH 100 would give DH 2135 and PH 100
        # see if multilevel nesting is needed
        if 'building' in raw_query:
            building = raw_query['building'][0]
            lec_building_query = Q('match', lectures__times__building = building)
            sec_building_query = Q('match', sections__times__building = building)
            query &= Q('bool', should=[Q('nested', query=lec_building_query, path='lectures.times', inner_hits={}),
                                       Q('nested', query=sec_building_query, path='sections.times', inner_hits={})])

        if 'room' in raw_query:
            room = raw_query['room'][0]
            lec_room_query = Q('match', lectures__times__room = room)
            sec_room_query = Q('match', sections__times__room = room)
            query &= Q('bool', should=[Q('nested', query=lec_room_query, path='lectures.times', inner_hits={}),
                                       Q('nested', query=sec_room_query, path='sections.times', inner_hits={})])

        if 'datetime' in raw_query:
            # raw_query['datetime'] is of type [arrow.arrow.Arrow]
            date_time = raw_query['datetime'][0].to('America/New_York')
            day = date_time.isoweekday() % 7
            time = date_time.time().strftime("%I:%M%p")
        
        # DEBUG
        print(json.dumps(query.to_dict(), indent=2))
        return query


def init_es_connection():
    connections.create_connection(hosts=ES_HOSTS,
                                  timeout=20,
                                  use_ssl=True,
                                  verify_certs=True,
                                  http_auth=ES_HTTP_AUTH)


def init_courses_output():
    output = {'response': {},
              'courses': []}
    return output


def format_courses_output(response):
    output = init_courses_output()
    output['response'] = response_to_dict(response)

    if has_error(response):
        return output
    for hit in response:
        output['courses'].append(hit.to_dict())

    return output


def has_error(response):
    if isinstance(response, dict) and response.get('status') is not None:
        return True
    return False


def response_to_dict(response):
    if isinstance(response, dict):
        return response
    else:
        return response.to_dict()


#
#
# @brief      Get the course by courseid.
#
# @param      courseid  (str) The courseid
# @param      term      (str) The elasticsearch index
#
# @return     A dictionary {courses: [<dictionary containing the course info>],
#             response: <response from the server> }
#
def get_course_by_id(courseid, term=None):
    output = {'response': {},
              'course': {}}
    index = term

    if re.search("^\d\d-\d\d\d$", courseid):
        searcher = CourseSearcher({'courseid': [courseid]}, index=index)
        response = searcher.execute()
        output['response'] = response_to_dict(response)

        if has_error(response):
            return output
        if response.hits.total != 0:
            # Got some hits
            output['course'] = response[0].to_dict()

    return output


#
#
# @brief      Get the course by instructor name.
#
# @param      name      (str) The instructor name
# @param      index     (str) The elasticsearch index
#
# @return     A dictionary {courses: [<dictionary containing the course info>],
#             response: <response from the server> }
#
def get_courses_by_instructor(name, index=None):
    searcher = CourseSearcher({'instructor': [name]}, index=index)
    response = searcher.execute()
    output = format_courses_output(response)
    return output


def get_courses_by_building_room(building, room, index=None):
    assert(building is not None or room is not None)
    raw_query = dict()
    if building is not None:
        raw_query['building'] = [building]
    if room is not None:
        raw_query['room'] = [room]
    searcher = CourseSearcher(raw_query, index=index)
    response = searcher.execute()
    output = format_courses_output(response)
    return output


def get_courses_by_datetime(date_time_str):
    try:
        date_time = arrow.get(date_time_str)
    except:
        output = init_courses_output()
        output['response'] = {
            'status': 400,
            'error': {
                'message': 'Failed to parse datetime. Please check format.'
            }
        }
        return output
    index = utils.get_index_from_date(date_time)
    searcher = CourseSearcher({'datetime': [date_time]}, index=index)
    response = searcher.execute()
    output = format_courses_output(response)
    return output


# def filterWithInnerHits(events, innerhits_hits_hits):
#     names = [hit['_source']['name'] for hit in innerhits_hits_hits]
#     names = set(names)
#     # print(innerhits_hits_hits)
#     filteredEvents = []
#     for event in events:
#         # print(event.lecsec)
#         if event.lecsec in names:
#             filteredEvents.append(event)
#     return filteredEvents


if __name__ == '__main__':
    init_es_connection()
