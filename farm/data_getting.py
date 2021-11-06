import mariadb
import redis
import json

from utils.constants import redis_server, redis_pw
from utils.db_connection import getCursor, commit

redis = redis.Redis(host= redis_server, password= redis_pw)

SEEDS = json.load(open("./resources/supported_seed_stats.json", "r"))
TREES = json.load(open("./resources/supported_tree_stats.json", "r"))
ANIMALS = json.load(open("./resources/supported_animal_stats.json", "r"))
DECORATIONS = json.load(open("./resources/supported_decoration_stats.json", "r"))

def getFarmData(request):
    token = request.headers.get("Authentication")

    if token:
        account_id = redis.hmget(token, ("id",))[0]
        
        try:
            query = "SELECT farmdata, coins, level, experience, cash FROM regular_farm JOIN " \
                "(SELECT farmer.id as sub_id, farmer.coins, farmer.level, farmer.experience, farmer.cash FROM farmer JOIN account " \
                "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                "ON regular_farm.owner_id = sub.sub_id"
            query_data = (account_id,)
            cursor = getCursor()
            cursor.execute(query, query_data)
            data = cursor.fetchone()
            returndata = {
                "farmdata": json.loads(data[0]),
                "coins": data[1],
                "level": data[2],
                "experience": data[3],
                "cash": data[4]
            }
            return returndata, 200
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Token missing from request", 401

def getSupportedSeeds(request):
    return SEEDS, 200

def getSupportedTrees(request):
    return TREES, 200

def getSupportedAnimals(request):
    return ANIMALS, 200

def getSupportedDecorations(request):
    return DECORATIONS, 200