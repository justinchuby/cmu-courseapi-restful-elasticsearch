import os
import ast


# A list of ES hosts
# Uncomment the following for debugging
# ES_HOSTS = ['https://c3d581bfab179c1101d5b7a9e22a5f95.us-east-1.aws.found.io:9243']
# ES_HTTP_AUTH = ("elastic:u3Mk8jjADYJ4NzUmPTn15MNx")

# Comment the following for debugging,
# or set corresponding environment variables
try:
    ES_HOSTS = ast.literal_eval(os.environ['ES_HOSTS'])
    ES_HTTP_AUTH = ast.literal_eval(os.environ['ES_HTTP_AUTH'])
except Exception as err:
    print(err)
    print("Please set ES_HOSTS and ES_HTTP_AUTH correctly.")

ES_COURSE_INDEX_PREFIX = 'course-'
