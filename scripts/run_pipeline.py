import os
import sys
import time
import psycopg2
import subprocess

DB_CONFIG = {
    'host': os.environ['DB_HOST'],
    'port': os.environ['DB_PORT'],
    'dbname': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD']
}

def wait_for_db(retries=10, delay=2):
    for i in range(retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("✅ Database ready")
            return
        except Exception:
            print(f"Waiting for DB... ({i+1}/{retries})")
            time.sleep(delay)
    raise Exception("Could not connect to database")

def run_sql_function(conn, func_call):
    with conn.cursor() as cur:
        cur.execute(func_call)
        return cur.fetchone()[0]

def main():
    start_all = time.time()
    wait_for_db()
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    try:
        # Проверяем, есть ли уже данные
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            count = cur.fetchone()[0]
        if count == 0:
            print("=== Generating test data ===")
            res1 = run_sql_function(conn, "SELECT generate_churn_data(100000, 3000000);")
            print(res1)
            conn.commit()
        else:
            print("=== Data already exists, skipping generation ===")

        print("=== Generating analytics charts ===")
        # Запускаем build_dashboard.py (он лежит в scripts)
        build_script = os.path.join(os.path.dirname(__file__), "build_dashboard.py")
        result = subprocess.run([sys.executable, build_script], capture_output=False)
        if result.returncode != 0:
            raise Exception("build_dashboard.py failed")

        print(f"✅ Pipeline finished in {time.time()-start_all:.2f} seconds")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()