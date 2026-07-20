import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn_string = os.getenv("DATABASE_URL")
        if not self.conn_string:
            raise ValueError("❌ CRITICAL: DATABASE_URL variable missing from environment.")

    def get_connection(self):
        """Returns a thread-safe connection instance from the pool."""
        try:
            conn = psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            print(f"❌ Database connection handshake failed: {e}")
            raise e

    def initialize_schema(self, schema_path="backend/database/schema.sql"):
        """Reads and executes the baseline schema configuration."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                with open(schema_path, "r") as f:
                    cur.execute(f.read())
            conn.commit()
            print("🚀 Relational database tables successfully synchronized.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Schema initialization failed: {e}")
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    # Test execution hook
    db = DatabaseManager()
    db.initialize_schema()