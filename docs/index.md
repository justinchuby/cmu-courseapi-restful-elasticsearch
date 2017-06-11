---
title: ScottyLabs Course API Online

---

## Introduction

ScottyLabs offers the Course API that provides information about CMU courses.
The documentation can be found [here](https://github.com/ScottyLabs/course-api).

This online version of the course-api is built with Flask and Elasticsearch.
The Flask server serves as a gateway between the client and the Elasticsearch
server (and potentially other databases). It translates requests into
Elasticsearch queries and returns scottylabs format course information to the
client.

### Try it out

[https://api.cmucoursefind.xyz/course/v1/course/21-259/](https://api.cmucoursefind.xyz/course/v1/course/21-259/) gives you the course
21-259 "Calculus in Three Dimensions".
[https://api.cmucoursefind.xyz/course/v1/instructor/kosbie/](https://api.cmucoursefind.xyz/course/v1/instructor/kosbie/) gives you courses
professor Kosbie teaches.

To explore the api, you can also go to [https://app.swaggerhub.com/apis/justinchuby/course-api/v1](https://app.swaggerhub.com/apis/justinchuby/course-api/v1) and try it out.


## Api Endpoint, Version 1

### GET `/course/:course-id`
The course endpoint returns a ScottyLabs Course Object defined in the Course
API, with extra fields `id`, `semester` and `rundate`. HTTP 404 is returned if
no such course is found.

`course-id` is the course number in the form `\d\d-\d\d\d`, e.g. 15-112.

There could also be wildcards in `course-id`. It is not yet implemented.

Sample Request:
```
GET https://api.cmucoursefind.xyz/course/v1/course/21-259/
```

Response format:
```json
{
    "course": <ScottyLabs Course Object>
}
```

Sample response:
```json
{
    "course": {
        "id": "21-259",
        "rundate": "2016-09-10",
        "prereqs_obj": {
            "invert": false,
            "reqs_list": [
                ["21-122"]
            ]
        },
        "department": "Mathematical Sciences",
        "coreqs": null,
        "lectures": [{
            "times": [{
                "begin": "09:30AM",
                "location": "Pittsburgh, Pennsylvania",
                "end": "10:20AM",
                "building": "WEH",
                "days": [1, 3, 5],
                "room": "7500"
            }],
            "instructors": ["Flaherty, Timothy"],
            "name": "Lec 1"
        }, {
            "times": [{
                "begin": "10:30AM",
                "location": "Pittsburgh, Pennsylvania",
                "end": "11:20AM",
                "building": "WEH",
                "days": [1, 3, 5],
                "room": "7500"
            }],
            "instructors": ["Flaherty, Timothy"],
            "name": "Lec 2"
        }],
        "prereqs": "21-122",
        "coreqs_obj": {
            "invert": null,
            "reqs_list": null
        },
        "sections": [{
            "times": [{
                "begin": "08:30AM",
                "location": "Pittsburgh, Pennsylvania",
                "end": "09:20AM",
                "building": "WEH",
                "days": [2],
                "room": "5320"
            }],
            "instructors": ["Liu, Pan"],
            "name": "A"
        }, {
            "times": [{
                "begin": "01:30PM",
                "location": "Pittsburgh, Pennsylvania",
                "end": "02:20PM",
                "building": "SH",
                "days": [2],
                "room": "219"
            }],
            "instructors": ["Satpathy, Siddharth"],
            "name": "D"
        }, {
            "times": [{
                "begin": "11:30AM",
                "location": "Pittsburgh, Pennsylvania",
                "end": "12:20PM",
                "building": "BH",
                "days": [2],
                "room": "255A"
            }],
            "instructors": ["Instructor TBA"],
            "name": "H"
        }],
        "semester": "Fall 2016",
        "units": 9.0,
        "desc": "Vectors, lines, planes, quadratic surfaces, polar, cylindrical and spherical coordinates, partial derivatives, directional derivatives, gradient, divergence, curl, chain rule, maximum-minimum problems, multiple integrals, parametric surfaces and curves, line integrals, surface integrals, Green-Gauss theorems. 3 hrs. lec., 1 hr. rec.",
        "name": "Calculus in Three Dimensions"
    }
}

```


### GET `/instructor/:name`
Courses taught by the instructor with `name`. An optional parameter `fuzzy` can
be added.

Sample Request:
```
GET https://api.cmucoursefind.xyz/course/v1/instructor/david%20kosbie/
```

Response format:
```json
{
    "courses": [<ScottyLabs Course Object>]
}
```
Notice the courses are now under `courses` and not `course` and are stored in
an array.


### GET `/datetime/:datetime`
Courses happening at given time. `datetime` should be in the format
defined by ISO-8601.

Sample Request:
```
GET https://api.cmucoursefind.xyz/course/v1/datetime/2017-06-01T17:00:00.000000-04:00/
```


### GET `/datetime/:datetime/timespan/:timespan`
Courses that start/happen within a span of time, starting from `datetime`.

`timespan` is the time span, in minutes, no more than 120 minutes.


### GET `/building/:building/term/:term`
`building` is the abbreviation of the building, for example, DH for Doherty
Hall, GHC for Gates and Hillman Centers. The legend can be found [here](http://www.cmu.edu/hub/legend.html).

`term` is required.


### GET `/building/:building/room/:room`
This allows you to get courses that are taught in a particular room.

Sample Request:
```
GET https://api.cmucoursefind.xyz/course/v1/building/dh/room/2315/
```


### GET `/room/:room/term/:term`

You can also get courses by the room number without know which building it is
in. This is handy when you just have the room number.

`term` is required


### GET `./term/:term`

`term` specifies the semester to look for. It is of the form `(f|s|m1|m2)\d{2}`,
for example, f17 (Fall 2017). It can also be `current` for the current term.

/term/:term can be appended after the `course`, `instructor`, `building`,
`room` and `building/room` endpoints.
