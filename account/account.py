import mariadb
import pandas
import redis
import secrets
from datetime import datetime, timezone

from utils.constants import server, user, pw, redis_server, redis_pw, TOKEN_LENGTH

redis = redis.Redis(host= redis_server, port= redis_pw)

def registerAccount(request):
    rjs = request.get_json()

    if "username" in rjs and "email" in rjs and "email2" in rjs and "passwordhash" in rjs and "passwordhash2" in rjs:
        if rjs["email"] != rjs["email2"]:
            return "Error creating account, 2 emails are not the same!", 500
        if rjs["passwordhash"] != rjs["passwordhash2"]:
            return "Error creating account, 2 passwords are not the same!", 500

        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Users")
        try:
            query = f"INSERT INTO account (username, email, passwordhash) VALUES (%s, %s, %s)"
            data = (rjs["username"], rjs["email"], rjs["passwordhash"])
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
            return "Success", 200
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Error creating account, data missing from account registration", 500

def loginAccount(request):
    rjs = request.get_json()

    if "email" in rjs and "passwordhash" in rjs:
        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Users")
        try:
            statement = "SELECT passwordhash FROM account WHERE email=%s"
            data = (rjs["email"],)
            cursor = conn.cursor()
            cursor.execute(statement, data)
            for (retrieved_passwordhash, ) in cursor:
                if retrieved_passwordhash == rjs["passwordhash"]:
                    token = secrets.token_urlsafe(TOKEN_LENGTH)
                    token_entry = {"token": token, "set-time": int(datetime.now(timezone.utc).timestamp())}
                    redis.hmset("email", token_entry)
                    return token, 200
                else:
                    return f"Wrong password!", 500
            return "Wrong password!", 500 # You're not supposed to know that this email doesn't exist in the database sssst
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Error logging in, data missing from login", 500

def changePassword(request):
    rjs = request.get_json()

    if "token" in rjs and "passwordhash" in rjs and "newpasswordhash" in rjs and "newpasswordhashrepeast" in rjs:
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