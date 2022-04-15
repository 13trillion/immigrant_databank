# @Author: Gutu, Bilal <Bilal_gutu>
# @Date:   2022-04-15T02:59:18-04:00
# @Last modified by:   Bilal_gutu
# @Last modified time: 2022-04-15T15:43:11-04:00


from sqlalchemy import *
from sqlalchemy.pool import NullPool


# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
# DB_USER = "brg2138"
# DB_PASSWORD = "Yay4111!"
#
# DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
#
# DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
#
#
# #
# # This line creates a database engine that knows how to connect to the URI above
# #
# engine = create_engine(DATABASEURI)
DB_USER = "brg2138"
DB_PASSWORD = "Yay4111!"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)
