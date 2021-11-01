import mariadb
import redis

from utils.constants import server, user, pw, redis_server, redis_pw

redis = redis.Redis(host= redis_server, password= redis_pw)

def getFarmData(request):
    token = request.headers.get("Authentication")

    if token:
        conn = mariadb.connect(user=user,
                               password=pw,
                               host=server,
                               port=3306,
                               database="Users")
        account_id = redis.hmget(token, ("id",))[0]
        
        try:
            query = "SELECT farmdata FROM regular_farm JOIN " \
                "(SELECT farmer.id as sub_id FROM farmer JOIN account " \
                "ON account.id = farmer.account_id WHERE farmer.account_id = %s) as sub " \
                "ON regular_farm.owner_id = sub.sub_id"
            query_data = (account_id,)
            cursor = conn.cursor()
            cursor.execute(query, query_data)
            farmdata = cursor.fetchone()[0]
            return farmdata, 200
        except Exception as e:
            return f"Error executing query, {e}", 500
    else:
        return "Token missing from request", 401