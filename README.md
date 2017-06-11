# cmu-courseapi-flask
The courseapi for CMU built with Flask and Elasticsearch

## Introduction

The online version of the course-api is built with Flask and Elasticsearch. This Flask server serves as a gateway between the client and the Elasticsearch server (and potentially other databases). It translates requests into Elasticsearch queries and returns scottylabs format course information to the client.

To set up the Elasticsearch server, follow steps on https://medium.com/@happymacaron/how-to-set-up-elasticsearch-on-openshift-405d0460c818 and https://github.com/justinchuby/cmu-courseapi-elasticsearch

## Current Progress

You may find the implemented endpoint in the `Api Endpoint` section.

### Try it out

https://swaggerhub.com/apis/justinchuby/course-api/v1.

## Requirements

```
Python>=3.5
flask
flask-restful
elasticsearch>=5.0.0,<6.0.0  # Elasticsearch 5.x
elasticsearch-dsl>=5.0.0,<6.0.0
arrow
certifi
```

## Api Endpoint Implementation

A more detailed description of the endpoint can be found
on https://justinchuby.github.io/cmu-courseapi-flask/.

```
GET

course/v1/
- [.]	/course/:course-id
	- [x]	:course-id: 15-112,
	- [ ]		15-*22, 15-*, *-122, 18-3*, 18-32*
- [.]	/instructor/:name
	- [x]	:name: first last, last, first
	- [x]	?fuzzy
- [x]	/datetime/:datetime
		# current happening classes at given time
		:datetime: in ISO 8601 format
- [x]	/datetime/:datetime/timespan/:timespan
		# gets courses that start/happen within a span of time
		:span: The time span, in minutes, no more than 120 minutes
- [x]	/building/:building/term/:term
		:building: DH
- [x]	/room/:room/term/:term
		:room: 2315
- [x]	/building/:building/room/:room
- [ ]	/search
		?q

- [x]	.../term/:term
		:term: f17, current
```

## Virtual Environment

`source venv/bin/activate`, `deactivate`
