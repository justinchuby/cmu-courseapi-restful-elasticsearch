import config.course

HOME_MESSAGE = 'Hoooray! You are connected.'
API_ROOT_MESSAGE = 'Course API by ScottyLabs!'
DATETIME_PARSE_FAIL = 'Failed to parse datetime. Please check format agrees with ISO-8601.'
SPAN_PARSE_FAIL = 'Failed to parse span. Span should be an integer between {} and {}.'.format(config.course.SPAN_LOWER_LIMIT, config.course.SPAN_UPPER_LIMIT)
EMPTY_SEARCH = 'At least provide one query parameter to search.'