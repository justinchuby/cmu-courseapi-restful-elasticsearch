# cmu-courseapi-flask
The courseapi for CMU built with flask

###
Api Endpoint

```
course/v1/
	/course/:course-id
		:course-id: 15-112, 15-*22, 15-*, *-122, 18-3*, 18-32*
	/instructor/:name
		:name: first last / last / first
		?fuzzy
	/time/:time
		# current happening classes at given time
	/building/:building
	/room/:room
		:room: e.g. 2315
	/building/:building/room/:room
	/search/?q=


Everything:
	/term/:term
		:term: f17
```
