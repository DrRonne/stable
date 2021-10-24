import mariadb
import pandas

from utils.constants import server, user, pw

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

def loginAccount(request):
    rjs = request.get_json()

    if "email" in rjs and "passwordhash" in rjs:
        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Tasks")
        try:
            statement = "SELECT passwordhash FROM users WHERE email=%s"
            data = (email,)
            cursor = conn.cursor()
            cursor.execute(statement, data)
            for (retrieved_passwordhash) in cursor:
                if retrieved_passwordhash == rjs["passwordhash"]:
                    return "Login succesful", 200
                else:
                    return "Wrong password!", 500
            return "Wrong password!", 500 # You're not supposed to know that this email doesn't exist in the database sssst
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Error logging in, data missing from login", 500

def changePassword(request):
    rjs = request.get_json()

    if "email" in rjs and "passwordhash" in rjs and "newpasswordhash" in rjs and "newpasswordhashrepeast" in rjs:
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