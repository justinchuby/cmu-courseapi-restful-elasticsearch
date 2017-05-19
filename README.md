# cmu-courseapi-flask
The courseapi for CMU built with Flask and Elasticsearch 5

## Introduction

The online version of the course-api is built with Flask and Elasticsearch. This Flask server serves as a gateway between the client and the Elasticsearch server (and potentially other databases). It translates requests into Elasticsearch queries and returns scottylabs format course information to the client.

## Current Progress

Working on setting up the ES 5 searver and queries constructor.

Currently the codebase is messy and nothing is working except the course detail endpoint. You may try it out by running `python3 api.py` and go to `http://localhost:5000/course/v1/course/15-112/` or `http://localhost:5000/course/v1/course/15-112/term/f17`.

## Development Requirements

```
Python>=3.5
flask
flask-restful
elasticsearch  # use version 2.x for now, will move to 5.x
elasticsearch-dsl  # use version 2.x for now, will move to 5.x
```

## Api Endpoint

```
GET

course/v1/
	/course/:course-id
		:course-id: 15-112, 15-*22, 15-*, *-122, 18-3*, 18-32*
	/instructor/:name
		:name: first last, last, first
		?fuzzy
	/time/:time
		# current happening classes at given time
	/building/:building
		:building: DH
	/room/:room
		:room: 2315
	/building/:building/room/:room
	/search
		?q

	.../term/:term
		:term: f17
```
