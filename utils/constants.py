import os

server = os.environ.get('DATABASE_SERVER')
user = os.environ.get('DATABASE_USER')
pw = os.environ.get('DATABASE_PW')
redis_server = os.environ.get('REDIS_SERVER')
redis_pw = os.environ.get('REDIS_PW')

TOKEN_LENGTH = 32