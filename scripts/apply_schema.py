import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
SCHEMA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "database", "schema.sql"
)


def apply_schema():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print(f"Reading schema file: {SCHEMA_FILE}")
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        print("Applying schema...")
        cur.execute(schema_sql)
        conn.commit()

        print("Schema applied successfully!")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error applying schema: {e}")


if __name__ == "__main__":
    apply_schema()
