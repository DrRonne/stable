import os

server = os.environ.get('DATABASE_SERVER')
user = os.environ.get('DATABASE_USER')
pw = os.environ.get('DATABASE_PW')
redis_server = os.environ.get('REDIS_SERVER')
redis_pw = os.environ.get('REDIS_PW')

TOKEN_LENGTH = 32

starter_farm_length = 20
starter_farm_width = 20
field_length = 4
field_width = 4

plow_cost = 15
plow_exp = 1