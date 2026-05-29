import os
import psycopg2
import pandas as pd

# Получаем параметры из окружения, если нет – используем значения по умолчанию (локальный запуск)
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5435'),
    'database': os.environ.get('DB_NAME', 'churn_db'),
    'user': os.environ.get('DB_USER', 'churn_user'),
    'password': os.environ.get('DB_PASSWORD', 'churn123')
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def query_to_df(sql):
    return pd.read_sql(sql, get_conn())