import datetime
import re
import copy
import json

import cmu_info, cmu_prof
from utils import *
from cmu_course import Course

import elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from elasticsearch_dsl.connections import connections
from config import ES_HOSTS, ES_HTTP_AUTH

ALL_COURSES_INDEX = "all_courses"

##
## @brief      The Searcher object that parses input and generates queries.
##
class Searcher(object):

    ##
    ## @brief      init
    ##
    ## @param      self
    ## @param      s           The query text
    ##
    def __init__(self, raw_query, index=None, size=5):
        self.raw_query = copy.deepcopy(raw_query)
        self.index = index
        self.size = size

    def __repr__(self):
        return "<Searcher Object: rawQuery={}>".format(repr(self.raw_query))

    def execute(self):
        # if index is None:
        #     index = ALL_COURSES_INDEX
        response = self.fetch(self.generate_query(), self.index, self.size)
        return response

    @staticmethod
    def fetch(query, index, size=200):
        s = Search(index=index).query(query)
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

        if 'courseid' in raw_query:
            query &= Q('term', id=raw_query['courseid'][0])

        if "instructor" in raw_query:
            instructor = " ".join(raw_query['instructor'])
            lec_name_query = Q('match', lectures__instructors=instructor)
            sec_name_query = Q('match', sections__instructors=instructor)

            query &= Q('bool', should=[Q('nested', query=lec_name_query, path='lectures', inner_hits={}),
                                       Q('nested', query=sec_name_query, path='sections', inner_hits={})])

        # DEBUG
        # print(query)
        return query


def init_es_connection():
    connections.create_connection(hosts=ES_HOSTS,
                                  timeout=20,
                                  use_ssl=True,
                                  verify_certs=True,
                                  http_auth=ES_HTTP_AUTH)


def init_output():
    output = {'response': {},
              'courses': []}
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
def get_courses_by_id(courseid, term=None):
    output = init_output()
    index = term
    if index is None:
        index = ALL_COURSES_INDEX

    if re.search("^\d\d-\d\d\d$", courseid):
        searcher = Searcher({'courseid': [courseid]})
        response = searcher.execute()
        output['response'] = response_to_dict(response)

        if has_error(response):
            return output
        if response.hits.total != 0:
            # Got some hits
            output['courses'].append(response[0].to_dict())

    return output


#
#
# @brief      Get the course by instructor name.
#
# @param      name      (str) The instructor name
# @param      index     (str) The elasticsearch index
#
# @return     A dictionary {course: <dictionary containing the course info>,
#             response: <response from the server> }
#
def get_courses_by_instructor(name, index=None):
    output = init_output()
    if index is None:
        index = ALL_COURSES_INDEX

    searcher = Searcher({'instructor': [name]})
    response = searcher.execute()
    output['response'] = response_to_dict(response)

    if has_error(response):
        return output

    for hit in response:
        output['courses'].append(hit.to_dict())
    return output


def filterWithInnerHits(events, innerhits_hits_hits):
    names = [hit['_source']['name'] for hit in innerhits_hits_hits]
    names = set(names)
    # print(innerhits_hits_hits)
    filteredEvents = []
    for event in events:
        # print(event.lecsec)
        if event.lecsec in names:
            filteredEvents.append(event)
    return filteredEvents
