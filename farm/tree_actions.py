import mariadb
import redis
import json
from datetime import datetime, timezone

from utils.constants import redis_server, redis_pw, tree_length, tree_width
from utils.db_connection import getCursor, commit

redis = redis.Redis(host= redis_server, password= redis_pw)

TREES = json.load(open("./resources/supported_tree_stats.json", "r"))

def plantTree(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        if "x" in rjs and "y" in rjs and "tree" in rjs:
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
                
                # Check if it's a valid spot
                for y in range(rjs["y"], rjs["y"] - tree_length, -1):
                    for x in range(rjs["x"], rjs["x"] - tree_width, -1):
                        if (rjs["y"] < 0 or rjs["y"] > len(farmdata["farm-grid"]) - 1 or
                            rjs["x"] < 0 or rjs["x"] > len(farmdata["farm-grid"][y]) - 1 or
                            farmdata["farm-grid"][y][x]):
                            return "Cannot plant here", 500

                # Check if item exists and if player can plant it (level and coins)
                tree_stats = next(item for item in TREES if item["name"] == rjs["tree"])
                if not tree_stats:
                    return "Tree doesn't exist", 500
                if not level >= tree_stats["level"]:
                    return "You don't have the required level to plant that", 500
                if not coins >= tree_stats["cost"]:
                    return "You don't have enough coins to plant that", 500
                
                lastHarvested = int(datetime.now(timezone.utc).timestamp())
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Tree",
                        "tree": rjs["tree"],
                        "lastHarvested": lastHarvested,
                        "queued": False,
                    }
                newcoins = coins - tree_stats["cost"]
                
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
                responsedata = {
                    'lastHarvested': lastHarvested
                }
                return responsedata, 200
            except Exception as e:
                return f"Error executing query, {e}", 500
        else:
            return "Tree data missing from request", 500
    else:
        return "Token missing from request", 401

def harvestTree(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        if "x" in rjs and "y" in rjs:
            account_id = redis.hmget(token, ("id",))[0]

            try:
                query = "SELECT coins, farmdata FROM regular_farm JOIN " \
                    "(SELECT farmer.coins, farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id"
                query_data = (account_id,)
                cursor = getCursor()
                cursor.execute(query, query_data)
                retrieved_data = cursor.fetchone()
                coins = retrieved_data[0]
                farmdata = json.loads(retrieved_data[1])

                currenttime = int(datetime.now(timezone.utc).timestamp())
                lastharvestedtime = farmdata["farm-grid"][rjs["y"]][rjs["x"]]["lastHarvested"]
                tree_stats = next(item for item in TREES if item["name"] == rjs["tree"])
                
                # Check if it's a valid spot
                if (not (farmdata["farm-grid"][rjs["y"]] and farmdata["farm-grid"][rjs["y"]][rjs["x"]] and
                    tree and lastharvestedtime <= currenttime - tree_stats["time"])):
                    return "Crop is not yet fully grown", 500

                # Check if item exists and if player can plant it (level and coins)
                if not tree_stats:
                    return "Tree doesn't exist", 500
                if not level >= tree_stats["level"]:
                    return "You don't have the required level to plant that", 500
                if not coins >= tree_stats["cost"]:
                    return "You don't have enough coins to plant that", 500
                
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Tree",
                        "tree": farmdata["farm-grid"][rjs["y"]][rjs["x"]]["tree"],
                        "lastHarvested": currenttime,
                        "queued": False,
                    }
                newcoins = coins + tree_stats["harvestcoins"]
                
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
                responsedata = {
                    'lastHarvested': lastHarvested
                }
                return responsedata, 200
            except Exception as e:
                return f"Error executing query, {e}", 500
        else:
            return "Tree data missing from request", 500
    else:
        return "Token missing from request", 401