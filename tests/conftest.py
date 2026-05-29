import pytest
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5435,
    'database': 'churn_db',
    'user': 'churn_user',
    'password': 'churn123'
}

@pytest.fixture
def db_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    yield conn
    conn.rollback()
    conn.close()