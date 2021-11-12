import mariadb
import redis
import json

from utils.constants import redis_server, redis_pw
from utils.db_connection import getCursor, commit
from utils.stats import calcLevel

redis = redis.Redis(host= redis_server, password= redis_pw)

DECORATIONS = json.load(open("./resources/supported_decoration_stats.json", "r"))

def placeDecoration(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        print(rjs)
        if "x" in rjs and "y" in rjs and "decoration" in rjs:
            account_id = redis.hmget(token, ("id",))[0]

            try:
                query = "SELECT level, coins, farmdata FROM regular_farm JOIN " \
                    "(SELECT farmer.level, farmer.coins, farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id"
                query_data = (account_id,)
                cursor = getCursor()
                cursor.execute(query, query_data)
                retrieved_data = cursor.fetchone()
                level = retrieved_data[0]
                coins = retrieved_data[1]
                farmdata = json.loads(retrieved_data[2])

                # Check if item exists and if player can plant it (level and coins)
                decoration_stats = next(item for item in DECORATIONS if item["name"] == rjs["decoration"])
                if not decoration_stats:
                    print(1)
                    return "Decoration doesn't exist", 500
                if not level >= decoration_stats["level"]:
                    print(2)
                    return "You don't have the required level to buy that", 500
                if not coins >= decoration_stats["cost"]:
                    print(3)
                    return "You don't have enough coins to buy that", 500
                
                # Check if it's a valid spot
                decoration_length = decoration_stats["length"]
                decoration_width = decoration_stats["width"]
                for y in range(rjs["y"], rjs["y"] - decoration_length, -1):
                    for x in range(rjs["x"], rjs["x"] - decoration_width, -1):
                        if (rjs["y"] < 0 or rjs["y"] > len(farmdata["farm-grid"]) - 1 or
                            rjs["x"] < 0 or rjs["x"] > len(farmdata["farm-grid"][y]) - 1 or
                            farmdata["farm-grid"][y][x]):
                            print(4)
                            return "Cannot place decoration here", 500
                
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Decoration",
                        "decoration": rjs["decoration"],
                        "queued": False,
                    }
                newcoins = coins - decoration_stats["cost"]
                
                updatequery = "UPDATE regular_farm JOIN " \
                    "(SELECT farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id " \
                    "SET farmdata = %s"
                updatedata = (account_id, json.dumps(farmdata))
                cursor.execute(updatequery, updatedata)
                farmerupdatequery = "UPDATE farmer JOIN account ON account.id = farmer.account_id " \
                    "SET coins = %s WHERE farmer.account_id = %s"
                farmerupdatedata = (newcoins, account_id)
                cursor.execute(farmerupdatequery, farmerupdatedata)
                commit()
                return "Placing ok", 200
            except Exception as e:
                print(e)
                return f"Error executing query, {e}", 500
        else:
            return "Decoration data missing from request", 500
    else:
        return "Token missing from request", 401