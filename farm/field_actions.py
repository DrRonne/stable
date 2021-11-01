import mariadb
import redis
import json
from datetime import datetime, timezone

from utils.constants import server, user, pw, redis_server, redis_pw, field_length, field_width, plow_cost, plow_exp
from utils.stats import calcLevel

redis = redis.Redis(host= redis_server, password= redis_pw)

SEEDS = json.load(open("./resources/supported_seed_stats.json", "r"))

def plowField(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        if "x" in rjs and "y" in rjs:
            conn = mariadb.connect(user=user,
                                password=pw,
                                host=server,
                                port=3306,
                                database="Users")
            account_id = redis.hmget(token, ("id",))[0]
            
            try:
                query = "SELECT farmdata, coins, level, experience FROM regular_farm JOIN " \
                    "(SELECT farmer.id as sub_id, farmer.coins, farmer.level, farmer.experience FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id"
                query_data = (account_id,)
                cursor = conn.cursor()
                cursor.execute(query, query_data)
                retrieved_data = cursor.fetchone()
                farmdata = json.loads(retrieved_data[0])
                coins = retrieved_data[1]
                level = retrieved_data[2]
                experience = retrieved_data[3]
                
                # Check if it's a valid spot
                for y in range(rjs["y"], rjs["y"] - field_length, -1):
                    for x in range(rjs["x"], rjs["x"] - field_width, -1):
                        if (rjs["y"] < 0 or rjs["y"] > len(farmdata["farm-grid"]) - 1 or
                            rjs["x"] < 0 or rjs["x"] > len(farmdata["farm-grid"][y]) - 1 or
                            (farmdata["farm-grid"][y][x] and farmdata["farm-grid"][y][x]["plown"])):
                            return "Error processing request, cannot plow here", 500
                # Check if player has enough cash
                if coins < plow_cost:
                    return "Error processing request, not enough coins", 500
                
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Field",
                        "seed": None,
                        "planted": None,
                        "fertilized": False,
                        "plown": True,
                        "queued": False,
                    }
                
                newcoins = coins - plow_cost
                newexperience = experience + plow_exp
                newlevel = calcLevel(newexperience)

                updatequery = "UPDATE regular_farm JOIN " \
                    "(SELECT farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id " \
                    "SET farmdata = %s"
                updatedata = (account_id, json.dumps(farmdata))
                cursor.execute(updatequery, updatedata)
                farmerupdatequery = "UPDATE farmer JOIN account ON account.id = farmer.account_id " \
                    "SET level = %s, experience = %s, coins = %s WHERE farmer.account_id = %s"
                farmerupdatedata = (newlevel, newexperience, newcoins, account_id)
                cursor.execute(farmerupdatequery, farmerupdatedata)
                conn.commit()
                return "Field plown", 200
            except Exception as e:
                return f"Error executing query, {e}", 500
        else:
            return "Field data missing from request", 500
    else:
        return "Token missing from request", 401

def plantSeed(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        if "x" in rjs and "y" in rjs:
            conn = mariadb.connect(user=user,
                                password=pw,
                                host=server,
                                port=3306,
                                database="Users")
            account_id = redis.hmget(token, ("id",))[0]
            
            try:
                query = "SELECT level, experience, coins, farmdata FROM regular_farm JOIN " \
                    "(SELECT farmer.level, farmer.experience, farmer.coins, farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id"
                query_data = (account_id,)
                cursor = conn.cursor()
                cursor.execute(query, query_data)
                retrieved_data = cursor.fetchone()
                level = retrieved_data[0]
                experience = retrieved_data[1]
                coins = retrieved_data[2]
                farmdata = json.loads(retrieved_data[3])
                
                # Check if it's a valid spot
                if (not (farmdata["farm-grid"][rjs["y"]] and farmdata["farm-grid"][rjs["y"]][rjs["x"]] and
                    not farmdata["farm-grid"][rjs["y"]][rjs["x"]]["seed"] and farmdata["farm-grid"][rjs["y"]][rjs["x"]]["plown"])):
                    return "Cannot plant here", 500

                # Check if item exists and if player can plant it (level and coins)
                seed_stats = next(item for item in SEEDS if item["name"] == rjs["seed"])
                if not seed_stats:
                    return "Seed doesn't exist", 500
                if not level >= seed_stats["level"]:
                    return "You don't have the required level to plant that", 500
                if not coins >= seed_stats["cost"]:
                    return "You don't have enough coins to plant that", 500
                
                planted = int(datetime.now(timezone.utc).timestamp())
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Field",
                        "seed": rjs["seed"],
                        "planted": planted,
                        "fertilized": False,
                        "plown": True,
                        "queued": False,
                    }
                newcoins = coins - seed_stats["cost"]
                newexperience = experience + seed_stats["experience"]
                newlevel = calcLevel(newexperience)
                
                updatequery = "UPDATE regular_farm JOIN " \
                    "(SELECT farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id " \
                    "SET farmdata = %s"
                updatedata = (account_id, json.dumps(farmdata))
                cursor.execute(updatequery, updatedata)
                farmerupdatequery = "UPDATE farmer JOIN account ON account.id = farmer.account_id " \
                    "SET level = %s, experience = %s, coins = %s WHERE farmer.account_id = %s"
                farmerupdatedata = (newlevel, newexperience, newcoins, account_id)
                cursor.execute(farmerupdatequery, farmerupdatedata)
                conn.commit()
                responsedata = {
                    'planted': planted
                }
                return responsedata, 200
            except Exception as e:
                return f"Error executing query, {e}", 500
        else:
            return "Field data missing from request", 500
    else:
        return "Token missing from request", 401