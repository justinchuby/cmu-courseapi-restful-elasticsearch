
## Introduction

ScottyLabs offers the Course API that provides information about CMU courses.
The documentation can be found [here](https://github.com/ScottyLabs/course-api)

This online version of the course-api is built with Flask and Elasticsearch.
The Flask server serves as a gateway between the client and the Elasticsearch
server (and potentially other databases). It translates requests into
Elasticsearch queries and returns scottylabs format course information to the
client.

### Try it out

https://api.cmucoursefind.xyz/course/v1/course/21-259/ gives you the course
21-259 "Calculus in Three Dimensions".
https://api.cmucoursefind.xyz/course/v1/instructor/kosbie/ gives you courses
professor Kosbie teaches.


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


### GET `/instructor/:name`
Courses taught by the instructor with <name>. An optional parameter `fuzzy` can
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
Notice the courses are now under `courses` and not `course` and are stores in
an array.


### GET `/datetime/:datetime`
Current classes happening at given time. `datetime` should be in the format
defined by ISO-8601.

Sample Request:
```
GET https://api.cmucoursefind.xyz/course/v1/datetime/2017-06-01T17:00:00.000000-04:00/
```

### GET `/datetime/:datetime/span/:span`
Gets courses that start/happen within a span of time, starting from `datetime`.

`span` is the time span, in minutes, no more than 120 minutes.

### GET `/building/:building/term/:term`
`building` is the abbreviation of the building, for example, DH for Doherty
Hall, GHC for Gates and Hillman Centers. The legend can be found on
http://www.cmu.edu/hub/legend.html.

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

### `./term/:term`

`term` specifies the semester to look for. It is of the form `(f|s|m1|m2)\d{2}`,
for example, f17 (Fall 2017). It can also be `current` for the current term.

/term/:term can be appended after the `course`, `instructor`, `building`,
`room` and `building/room` endpoints.
