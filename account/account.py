import mariadb
import redis
import secrets
import bcrypt
import json
from datetime import datetime, timezone

from utils.constants import server, user, pw, redis_server, redis_pw, TOKEN_LENGTH, starter_farm_length, starter_farm_width

redis = redis.Redis(host= redis_server, password= redis_pw)

def registerAccount(request):
    rjs = request.get_json()

    if "username" in rjs and "email" in rjs and "email2" in rjs and "password" in rjs and "password2" in rjs:
        if rjs["email"] != rjs["email2"]:
            return "Error creating account, 2 emails are not the same!", 500
        if rjs["password"] != rjs["password2"]:
            return "Error creating account, 2 passwords are not the same!", 500

        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Users")
        try:
            statement = "SELECT COUNT(id) FROM account WHERE email=%s OR username=%s"
            data = (rjs["email"], rjs["username"])
            cursor = conn.cursor()
            cursor.execute(statement, data)
            if cursor.fetchone()[0] == 0:
                try:
                    query = "INSERT INTO account (username, email, passwordhash) VALUES (%s, %s, %s)"
                    hashed = bcrypt.hashpw(rjs["password"].encode('utf8'), bcrypt.gensalt())
                    data = (rjs["username"], rjs["email"], hashed)
                    cursor = conn.cursor()
                    cursor.execute(query, data)
                    conn.commit()

                    accountfetchquery = "SELECT id FROM account WHERE username=%s AND email=%s and passwordhash=%s"
                    cursor.execute(accountfetchquery, data)
                    account_id = cursor.fetchone()[0]

                    farmerquery = "INSERT INTO farmer (account_id) VALUES (%s)"
                    farmerdata = (account_id,)
                    cursor.execute(farmerquery, farmerdata)
                    conn.commit()

                    farmerfetchquery = "SELECT id FROM farmer WHERE account_id=%s"
                    cursor.execute(farmerfetchquery, farmerdata)
                    farmer_id = cursor.fetchone()[0]

                    farmquery = "INSERT INTO regular_farm (owner_id, farmdata) VALUES (%s, %s)"
                    starter_farm = {
                        "farm-name": rjs["username"] + "'s farm",
                        "farm-width": starter_farm_width,
                        "farm-height": starter_farm_length,
                        "farm-grid": []
                    }
                    for y in range(0, starter_farm_length):
                        starter_farm["farm-grid"].append([])
                        for x in range(0, starter_farm_width):
                            starter_farm["farm-grid"][y].append(None)
                    farmdata = (farmer_id, json.dumps(starter_farm))
                    cursor.execute(farmquery, farmdata)
                    conn.commit()
                    return "Success", 200
                except Exception as e:
                    return f"Error executing query, {e}", 500
            else:
                return f"Username or email address already in use!", 500
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Error creating account, data missing from account registration", 500

def loginAccount(request):
    rjs = request.get_json()

    if "email" in rjs and "password" in rjs:
        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Users")
        try:
            statement = "SELECT id, passwordhash FROM account WHERE email=%s"
            data = (rjs["email"],)
            cursor = conn.cursor()
            cursor.execute(statement, data)
            for (retrieved_id, retrieved_passwordhash) in cursor:
                if bcrypt.checkpw(rjs["password"].encode('utf8'), retrieved_passwordhash.encode('utf8')):
                    token = secrets.token_urlsafe(TOKEN_LENGTH)
                    token_entry = {"id": retrieved_id, "set-time": int(datetime.now(timezone.utc).timestamp())}
                    redis.hmset(token, token_entry)
                    return token, 200
                else:
                    return f"Wrong password!", 500
            return "Wrong password!", 500 # You're not supposed to know that this email doesn't exist in the database sssst
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Error logging in, data missing from login", 500

def logoutAccount(request):
    token = request.headers.get("Authentication")

    if token:
        try:
            redis.hdel(token, "email", "set-time")
        except Exception as e:
            return f"Error login out, {e}", 500
    else:
        return "Error loging out, token missing from logout", 500

# REALLY UNFINISHED
def changePassword(request):
    rjs = request.get_json()
    token = request.headers.get("Authentication")

    if token and "passwordhash" in rjs and "newpasswordhash" in rjs and "newpasswordhashrepeast" in rjs:
        if rjs["newpasswordhash"] != rjs["newpasswordhashrepeat"]:
            return "Error changing password, 2 passwords don't match!", 500

        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Tasks")
        try:
            query = f"INSERT INTO users (username, email, passwordhash) VALUES (%s, %s, %s)"
            data = (rjs["username"], rjs["email"], rjs["passwordhash"])
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return "Success", 200
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Error creating account, data missing from account registration", 500