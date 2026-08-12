import psycopg2
from psycopg2 import pool
from pgvector.psycopg2 import register_vector

DB_CONFIG = {
    "dbname": "edusphere_db",
    "user": "sumanasripola",
    "password": "Sumana_1425",
    "host": "localhost",
    "port": 5432,
}

connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)


def get_conn():
    conn = connection_pool.getconn()
    register_vector(conn)
    return conn


def release_conn(conn):
    connection_pool.putconn(conn)
