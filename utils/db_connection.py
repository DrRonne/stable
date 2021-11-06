import mariadb

from utils.constants import server, user, pw

conn = mariadb.connect(user=user,
                        password=pw,
                        host=server,
                        port=3306,
                        database="Users")

def getCursor():
    return conn.cursor()

def commit():
    conn.commit()