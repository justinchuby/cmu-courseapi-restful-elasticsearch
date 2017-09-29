import os
import ast


# A list of ES hosts
# Uncomment the following for debugging
# ES_HOSTS = ['https://c3d581bfab179c1101d5b7a9e22a5f95.us-east-1.aws.found.io:9243']
# ES_HTTP_AUTH = ("elastic:u3Mk8jjADYJ4NzUmPTn15MNx")

# Comment the following for debugging,
# or set corresponding environment variables

# Set service type, AWS or default
SERVICE = 'AWS'


AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
AWS_REGION = ''
ES_HTTP_AUTH = ''

try:
    if SERVICE == 'AWS':
        AWS_ES_HOSTS = ast.literal_eval(os.environ['AWS_ES_HOSTS'])
        AWS_ACCESS_KEY = ast.literal_eval(os.environ['AWS_ACCESS_KEY'])
        AWS_SECRET_KEY = ast.literal_eval(os.environ['AWS_SECRET_KEY'])
        AWS_REGION = ast.literal_eval(os.environ['AWS_REGION'])
    else:
        ES_HOSTS = ast.literal_eval(os.environ['ES_HOSTS'])
        ES_HTTP_AUTH = ast.literal_eval(os.environ['ES_HTTP_AUTH'])
except Exception as err:
    print(err)
    print("Please configure ES service in es_config.py correctly.")

ES_COURSE_INDEX_PREFIX = 'course-'
ES_FCE_INDEX = 'fce'
