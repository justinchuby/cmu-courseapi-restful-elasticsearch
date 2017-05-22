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
    def __init__(self, raw_query):
        self.raw_query = copy.deepcopy(raw_query)

    def __repr__(self):
        return "<Searcher Object: rawQuery={}>".format(repr(self.raw_query))

    ##
    ## @brief      Generate the query for the database.
    ##
    ## @return     (dict) The query for querying the database.
    ##
    def generate_query(self):
        return self.constructESQueryFromRaw(self.raw_query)

    @staticmethod
    def constructESQueryFromRaw(raw_query):
        if 'rest' in raw_query:
            pass
            # query["query"]["bool"]["must"] = {"query_string": {
            #                                     "query": raw_query["rest"][0]}}
            # query["query"]["bool"]["should"] = [
            #                                     {"match": {"id": raw_query["rest"][0]}},
            #                                     {"match": {"name": raw_query["rest"][0]}}
            #                                     ]
        elif 'courseid' in raw_query:
            query = Q('term', id=raw_query['courseid'][0])

        # else:
        #     query["query"]["bool"]["must"] = {"match_all": {}}

        # # fields: day, building, room, instructor
        # if "day" in raw_query: # must
        #     query["query"]["bool"]["filter"]["or"][0]\
        #          ["nested"]["query"]["bool"]["must"]\
        #          ["nested"]["query"]["bool"]["must"].append(
        #             {"match": {"lectures.times.days": raw_query["day"][0]}})
        #     query["query"]["bool"]["filter"]["or"][1]\
        #          ["nested"]["query"]["bool"]["must"]\
        #          ["nested"]["query"]["bool"]["must"].append(
        #             {"match": {"sections.times.days": raw_query["day"][0]}})

        # if "building" in raw_query: # must
        #     query["query"]["bool"]["filter"]["or"][0]\
        #          ["nested"]["query"]["bool"]["must"]\
        #          ["nested"]["query"]["bool"]["must"].append(
        #             {"match": {"lectures.times.building": raw_query["building"][0]}})
        #     query["query"]["bool"]["filter"]["or"][1]\
        #          ["nested"]["query"]["bool"]["must"]\
        #          ["nested"]["query"]["bool"]["must"].append(
        #             {"match": {"sections.times.building": raw_query["building"][0]}})

        # if "room" in raw_query: # must
        #     query["query"]["bool"]["filter"]["or"][0]\
        #          ["nested"]["query"]["bool"]["must"]\
        #          ["nested"]["query"]["bool"]["must"].append(
        #             {"match": {"lectures.times.room": raw_query["room"][0]}})
        #     query["query"]["bool"]["filter"]["or"][1]\
        #          ["nested"]["query"]["bool"]["must"]\
        #          ["nested"]["query"]["bool"]["must"].append(
        #             {"match": {"sections.times.room": raw_query["room"][0]}})

        if "instructor" in raw_query: # should
        #     for i in range(0, 2):
        #         query["query"]["bool"]["filter"]["or"][i]\
        #              ["nested"]["query"]["bool"]["should"] = []

        #     query["query"]["bool"]["filter"]["or"][0]\
        #          ["nested"]["query"]["bool"]["should"].append(
        #             {"match": {"lectures.instructors": raw_query["instructor"][0]}})
        #     query["query"]["bool"]["filter"]["or"][1]\
        #          ["nested"]["query"]["bool"]["should"].append(
        #             {"match": {"sections.instructors": raw_query["instructor"][0]}})


        return query


class Parser(object):
    def __init__(self, text):
        text = text.strip()
        if len(text) > 140:
            self.text = text[:140]
        else:
            self.text = text
        self.raw_query = Listdict()
        self.searchable = splitString(self.text.lower(), " ")
        self.length = len(self.searchable)
        self.parse()

    def __repr__(self):
        return "<Parser Object: text={}, rawQuery={}>".format(repr(self.text), repr(self.raw_query))


    ##
    ## @brief      Constructs the query for a given field.
    ##
    ## @param      s      (str) Input text
    ## @param      field  (str) The specified field type
    ##
    ## @return     Returns a dictionary of results with field as the key.
    ##
    @staticmethod
    def getField(s, field):
        result = dict()
# DEBUG
        # print("##s:", s, field)
        # Match course id in forms of "36217" or "36-217"
        if field == "courseid":
            if s.isdigit():
                if len(s) == 5:
                    result[field] = [(s[:2] + "-" + s[2:])]
            else:
                match = re.search("\d\d-\d\d\d", s)
                if match:
                    result[field] = [match.group()]
                else:
                    return None

        # Match building in forms of "BH136A"
        if field == "building_room":
            match = re.search("^([a-zA-Z]{2})(\w?\d+\w?)", s)
            # "BH136A", "HHA104"
            if match:
                if match.group(1) in cmu_info.CMU_BUILDINGS_ABBR:
                    result["building"] = [match.group(1).upper()]
                    result["room"] = [match.group(2).upper()]
            # "GHC4102"
                else:
                    match = re.search("^([a-zA-Z]{3})(\w?\d+\w?)", s)
                    if match:
                        result["building"] = [match.group(1).upper()]
                        result["room"] = [match.group(2).upper()]
            if not match:
                return None

        if field == "building":
            if s in cmu_info.CMU_BUILDINGS:
                result[field] = [cmu_info.CMU_BUILDINGS[s]]
            elif s in cmu_info.CMU_BUILDINGS_ABBR:
                result[field] = [s.upper()]
            else:
                return None

        if field == "day":
            if s in cmu_info.DAYS_STRING:
                result[field] = [cmu_info.DAYS_STRING[s]]
            else:
                return None

        if field == "instructor":
            # see if the string is a part of the name of a instructor
            # could be first name or last name or both
            if s in cmu_prof.NAMES:
                result[field] = [s]
            else:
                return None

        return result if result != dict() else None

    ##
    ## @brief      Gets the query for a specified from the searchable list
    ##
    ## @param      self        The object
    ## @param      searchable  The searchable list consists of strings as
    ##                         elements
    ## @param      field       The specified field
    ## @param      multiple  Whether or not to look for multiple results
    ##
    ## @return     A list of query strings if found, None if nothing is found.
    ##
    def getFieldFromList(self, searchable, field):
# DEBUG
        # print("##s's:", searchable, field)

        # the fields below are not popped
        dontPopFields = {"courseid"}
        founds = Listdict()
        i = 0
        while i < len(searchable):
            found = self.getField(searchable[i], field)
            if found:
                # found a valid search condition matching the specified field
                if not (field in dontPopFields):
                    searchable.pop(i)
                    i -= 1  # step back because of the popped searchable
                founds.concat(found)
            i += 1  # next searchable
        return founds

    ##
    ## @brief      Gets rid of the empty queries in the rawQuery.
    ##
    def cleanUpRawQuery(self):
        keys = list(self.raw_query.keys())
        for key in keys:
            value = self.raw_query[key]
            if type(value) == list:
                self.raw_query[key] = [elem for elem in value if elem != ""]
                value = self.raw_query[key]
            if containsNone(value) or value == [] or value == "":
                del self.raw_query[key]

    ##
    ## @brief      Uses the searchable to generate field of search for constructing a query.
    ##
    ## @return     None
    ##
    def parse(self):
        # converts the time into datetime format
        searchable = copy.copy(self.searchable)
        if self.length == 0:
            return None

        if self.length == 1:
            s = searchable[0]
            # it might be a course name, a course id, a room courseid,
            # (a building name),
            # or a building and room combined

            # course id
            try: self.raw_query["courseid"] = self.getField(s, "courseid")["courseid"]
            except TypeError: pass

            # building and room combined
            _building_room = self.getField(s, "building_room")
            if _building_room:
                self.raw_query.concat(_building_room)

            if s.isalpha():
                # might be a day
                try: self.raw_query["day"] = self.getField(s, "day")["day"]
                except TypeError: pass
                # might be a building name
                try: self.raw_query["building"] = self.getField(s, "building")["building"]
                except TypeError: pass
                # might be an instructor's name
                try: self.raw_query["instructor"] = self.getField(s, "instructor")["instructor"]
                except TypeError: pass

            self.cleanUpRawQuery()
            if self.raw_query == dict():
                self.raw_query["rest"] = [s]

        else:
            _building_room = self.getFieldFromList(searchable, "building_room")
            if _building_room:
                self.raw_query.concat(_building_room)
            else:
                self.raw_query["building"] = self.getFieldFromList(searchable, "building").get("building")
                self.raw_query["room"] = self.getFieldFromList(searchable, "room").get("room")
            self.raw_query["courseid"] = self.getFieldFromList(searchable, "courseid").get("courseid")
            self.raw_query["day"] = self.getFieldFromList(searchable, "day").get("day")
            self.raw_query["rest"] = [" ".join(searchable)]

        self.cleanUpRawQuery()


def init_es_connection():
    connections.create_connection(hosts=['https://c3d581bfab179c1101d5b7a9e22a5f95.us-east-1.aws.found.io:9243'],
                                  timeout=20,
                                  use_ssl=True,
                                  verify_certs=True,
                                  http_auth=("elastic:u3Mk8jjADYJ4NzUmPTn15MNx"))


def query_course(query, index=None):
    if index is None:
        index = ALL_COURSES_INDEX
    response = fetch(index, query, size=5)
    return response


def fetch(index, query, size=200):
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


def has_error(response):
    if isinstance(response, dict) and response.get('status') is not None:
        return True
    return False

##
## @brief      Get the course by courseid.
##
## @param      courseid  (str) The courseid
## @param      term     (str) The elasticsearch index
##
## @return     A dictionary
#              {course: <dictionary containing the course info>,
#               response: <response from the server>
#              }
#
def get_course_by_id(courseid, term=None):
    output = {'response': {},
              'course': None}
    index = term
    if index is None:
        index = ALL_COURSES_INDEX
    if re.search("^\d\d-\d\d\d$", courseid):
        searcher = Searcher({'courseid': [courseid]})
        query = searcher.generate_query()
        response = query_course(query, index=index)
        output['response'] = response.to_dict()

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
# @param      courseid  (str) The courseid
# @param      index     (str) The elasticsearch index
#
# @return     A dictionary {course: <dictionary containing the course info>,
#             response: <response from the server> }
#
def get_course_by_instructor(name, index=None):
    output = {'response': {},
              'course': None}
    if index is None:
        index = ALL_COURSES_INDEX


# here





    # query = searcher.generate_query()
    # response = query_course(query, index=index)
    output['response'] = response
    if response.get("status") is not None:
        return output
    print(response)
    assert(False)
    if "hits" in response and response['hits']['hits'] != []:
        output['course'] = response['hits']['hits'][0]['_source']
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
