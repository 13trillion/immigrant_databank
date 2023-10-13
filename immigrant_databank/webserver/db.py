# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T02:59:18-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-18T21:40:55-04:00


from sqlalchemy import *
from sqlalchemy.pool import NullPool


def get_db():
    DB_USER = ""
    DB_PASSWORD = ""

    DB_SERVER = ""

    DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
    #
    # This line creates a database engine that knows how to connect to the URI above
    #
    engine = create_engine(DATABASEURI)

    connection = engine.connect()

    return connection


def close_db(conn):
    conn.close()
