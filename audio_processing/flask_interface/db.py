import psycopg2
import psycopg2.pool

from . import config



connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20, **config.DATABASE_CONFIG
)

def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)