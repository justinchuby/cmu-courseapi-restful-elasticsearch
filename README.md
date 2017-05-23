# cmu-courseapi-flask
The courseapi for CMU built with Flask and Elasticsearch 5

## Introduction

The online version of the course-api is built with Flask and Elasticsearch. This Flask server serves as a gateway between the client and the Elasticsearch server (and potentially other databases). It translates requests into Elasticsearch queries and returns scottylabs format course information to the client.

## Current Progress

Working on setting up the ES 5 searver and queries constructor.

You may find the implemented endpoint in the `Api Endpoint` section. You can try it out by running `python3 api.py` and go to `http://localhost:5000/course/v1/course/15-112/` or `http://localhost:5000/course/v1/course/15-112/term/f17`.

## Development Requirements

```
Python>=3.5
flask
flask-restful
elasticsearch-dsl>=5.0.0,<6.0.0  # Elasticsearch 5.x
elasticsearch-dsl>=5.0.0,<6.0.0
arrow
```

## Api Endpoint

```
GET

course/v1/
- [.]	/course/:course-id
	- [x]	:course-id: 15-112,
	- [ ]		15-*22, 15-*, *-122, 18-3*, 18-32*
- [.]	/instructor/:name
	- [x]	:name: first last, last, first
	- [ ]	?fuzzy
- [x]	/datetime/:datetime
			# current happening classes at given time
- [x]	/building/:building
			:building: DH
- [x]	/room/:room
			:room: 2315
- [x]	/building/:building/room/:room
- [ ]	/search
			?q

- [.]	.../term/:term
			:term: f17
```
