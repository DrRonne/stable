import mariadb
import redis
import json
from datetime import datetime, timezone

from utils.constants import redis_server, redis_pw
from utils.db_connection import getCursor, commit
from utils.stats import calcLevel

redis = redis.Redis(host= redis_server, password= redis_pw)

ANIMALS = json.load(open("./resources/supported_animal_stats.json", "r"))

def placeAnimal(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        if "x" in rjs and "y" in rjs and "animal" in rjs:
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
                animal_stats = next(item for item in ANIMALS if item["name"] == rjs["animal"])
                if not animal_stats:
                    print(1)
                    return "Animal doesn't exist", 500
                if not level >= animal_stats["level"]:
                    print(2)
                    return "You don't have the required level to buy that", 500
                if not coins >= animal_stats["cost"]:
                    print(3)
                    return "You don't have enough coins to buy that", 500
                
                # Check if it's a valid spot
                animal_length = animal_stats["length"]
                animal_width = animal_stats["width"]
                for y in range(rjs["y"], rjs["y"] - animal_length, -1):
                    for x in range(rjs["x"], rjs["x"] - animal_width, -1):
                        if (rjs["y"] < 0 or rjs["y"] > len(farmdata["farm-grid"]) - 1 or
                            rjs["x"] < 0 or rjs["x"] > len(farmdata["farm-grid"][y]) - 1 or
                            farmdata["farm-grid"][y][x]):
                            print(4)
                            return "Cannot place animal here", 500
                
                lastHarvested = int(datetime.now(timezone.utc).timestamp())
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Animal",
                        "animal": rjs["animal"],
                        "lastHarvested": lastHarvested,
                        "queued": False,
                    }
                newcoins = coins - animal_stats["cost"]
                
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
                print(e)
                return f"Error executing query, {e}", 500
        else:
            return "Animal data missing from request", 500
    else:
        return "Token missing from request", 401

def harvestAnimal(request):
    token = request.headers.get("Authentication")

    if token:
        rjs = request.get_json()
        if "x" in rjs and "y" in rjs:
            account_id = redis.hmget(token, ("id",))[0]

            try:
                query = "SELECT level, experience, coins, farmdata FROM regular_farm JOIN " \
                    "(SELECT farmer.level, farmer.experience, farmer.coins, farmer.id as sub_id FROM farmer JOIN account " \
                    "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                    "ON regular_farm.owner_id = sub.sub_id"
                query_data = (account_id,)
                cursor = getCursor()
                cursor.execute(query, query_data)
                retrieved_data = cursor.fetchone()
                level = retrieved_data[0]
                experience = retrieved_data[1]
                coins = retrieved_data[2]
                farmdata = json.loads(retrieved_data[3])

                currenttime = int(datetime.now(timezone.utc).timestamp())
                lastharvestedtime = farmdata["farm-grid"][rjs["y"]][rjs["x"]]["lastHarvested"]
                animal_stats = next(item for item in ANIMALS if item["name"] == farmdata["farm-grid"][rjs["y"]][rjs["x"]]["animal"])
                
                if (not "time" in animal_stats or not animal_stats["time"]):
                    return "Animal not harvestable", 500

                # Check if it's a valid spot
                if (not (farmdata["farm-grid"][rjs["y"]] and farmdata["farm-grid"][rjs["y"]][rjs["x"]] and
                    animal_stats and lastharvestedtime <= currenttime - animal_stats["time"])):
                    return "Animal not ready to harvest", 500
                
                farmdata["farm-grid"][rjs["y"]][rjs["x"]] = {
                        "type": "Animal",
                        "animal": farmdata["farm-grid"][rjs["y"]][rjs["x"]]["animal"],
                        "lastHarvested": currenttime,
                        "queued": False,
                    }
                newcoins = coins
                if animal_stats["harvestcoins"]:
                    newcoins += animal_stats["harvestcoins"]
                newexperience = experience
                if animal_stats["experience"]:
                    newexperience += animal_stats["experience"]
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
                commit()
                responsedata = {
                    'lastHarvested': currenttime
                }
                return responsedata, 200
            except Exception as e:
                return f"Error executing query, {e}", 500
        else:
            return "Animal data missing from request", 500
    else:
        return "Token missing from request", 401