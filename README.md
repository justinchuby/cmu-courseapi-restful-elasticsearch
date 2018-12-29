# cmu-courseapi-flask
The courseapi for CMU built with Flask and Elasticsearch

## Introduction

The online version of the course-api is built with Flask and Elasticsearch. This Flask server serves as a gateway between the client and the Elasticsearch server (and potentially other databases). It translates requests into Elasticsearch queries and returns scottylabs format course information to the client.

To set up the Elasticsearch server, you may use the Elasticsearch service on AWS.

## Current Progress

Currently I am working on compability with MongoDB.

### Try it out

https://swaggerhub.com/apis/justinchuby/course-api/v1.

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
- [x]	/search
		?q

- [x]	.../term/:term
		:term: f17, current
```

## Virtual Environment

`source venv/bin/activate`, `deactivate`
